import re
from bs4 import BeautifulSoup
from datetime import datetime

from app.models.car import CarListing
from app.utils.parsers import parse_price, parse_int, parse_float, parse_mileage
from app.utils.extractors import extract_title, extract_manufactured_year, build_model_name
from app.utils.finance import calculate_loan_term, calculate_monthly, calculate_car_age_months


CURRENT_YEAR = datetime.now().year


def parse_listing(html: str, url: str) -> CarListing:
    """
    Converts raw SGCarMart HTML into a structured CarListing.
    """

    soup = BeautifulSoup(html, "html.parser")
    missing_fields: list[str] = []

    raw = {}

    # Extract title using multiple strategies
    raw["Title"] = extract_title(soup)

    # Extract generic detail blocks
    items = soup.find_all("div", class_=re.compile(r"styles_item__"))
    for item in items:
        title = item.find("div", class_=re.compile(r"styles_detailTitle__"))
        value = item.find("div", class_=re.compile(r"styles_descContainer__"))
        if title and value:
            raw[title.text.strip()] = value.get_text(" ", strip=True)

    # Extract Category
    category_items = soup.find_all("div", class_=re.compile(r"styles_item__"))
    for item in category_items:
        title_div = item.find("div", class_=re.compile(r"styles_titleContainer__"))
        if title_div and title_div.text.strip() == "Category":
            desc_div = item.find("div", class_=re.compile(r"styles_descContainer__"))
            if desc_div:
                raw["Category"] = desc_div.get_text(strip=True)
            break

    # Manufactured year with fallbacks
    manufactured_year = extract_manufactured_year(raw)

    # Type
    car_type = raw.get("Category", "").split(",")[0] if raw.get("Category") else None

    # ARF & rebate logic
    arf = parse_price(raw.get("ARF", ""), missing_fields, "ARF")
    if manufactured_year and arf and manufactured_year >= CURRENT_YEAR - 10:
        end_rebate = min(arf / 2, 60000)
    else:
        end_rebate = 0.0

    # Price
    price = parse_price(raw.get("Price", ""), missing_fields, "Price")

    # Power parsing
    curb_weight = parse_float(raw.get("Curb Weight", ""), missing_fields, "Curb Weight")
    power_str = raw.get("Power", "")
    power_bhp = None
    power_kw = None

    if power_str and "(" in power_str and power_str not in ["N.A.", "N.A"]:
        try:
            power_kw = float(power_str.split(" kW")[0])
            bhp_str = power_str.split("(")[1].replace(")", "").strip()
            power_bhp = int(float(bhp_str.split(" ")[0]))
        except (ValueError, IndexError):
            missing_fields.append("Power")
    else:
        missing_fields.append("Power")

    power_to_weight = None
    if curb_weight and power_bhp:
        power_to_weight = round(power_bhp / curb_weight * 1000, 2)

    # Engine CC
    engine_cap = raw.get("Engine Cap", "")
    engine_cc = int(engine_cap.split(" cc")[0].replace(",", "")) if engine_cap else None

    # Reg date and age
    reg_date_full = raw.get("Reg Date", "")
    reg_date_str = reg_date_full.split(" ")[0].replace("-", " ") if reg_date_full else None

    # age_months = None
    # if reg_date_str and reg_date_str not in ["N.A.", "N.A", ""]:
    #     age_months = calculate_car_age_months(reg_date_str)
    # else:
    #     missing_fields.append("Reg Date")

    # Extract COE left from reg date string
    coe_left = None
    coe_left_str = None
    coe_left_months = None

    if "(" in reg_date_full:
        try:
            coe_part = reg_date_full.split("(")[1].split(" COE left")[0].strip()
            coe_left = coe_part

            # Use regex to extract years and months regardless of format
            years_match = re.search(r"(\d+)\s*(?:y|yr|yrs|year|years)", coe_left, re.IGNORECASE)
            months_match = re.search(r"(\d+)\s*(?:m|mth|mths|month|months)", coe_left, re.IGNORECASE)

            years = int(years_match.group(1)) if years_match else 0
            months = int(months_match.group(1)) if months_match else 0

            coe_left_months = years * 12 + months

            if coe_left_months == 0 and not years_match and not months_match:
                missing_fields.append(f"COE Left (no valid pattern found in: {coe_left})")
                coe_left_months = None

            coe_left_str = f"{years} year(s) {months} month(s)"
        except Exception:
            missing_fields.append("COE Left (parsing error)")

    # Loan term and monthly calculations
    loan_term = calculate_loan_term(coe_left_months) if coe_left_months else None

    zero_dp = calculate_monthly(price, loan_term, 0.0, 4.98) if price and loan_term else None
    dp_10k = calculate_monthly(price, loan_term, 10000.0, 4.0) if price and loan_term else None
    dp_20k = calculate_monthly(price, loan_term, 20000.0, 3.5) if price and loan_term else None
    dp_30k = calculate_monthly(price, loan_term, 30000.0, 3.5) if price and loan_term else None
    dp_40k = calculate_monthly(price, loan_term, 40000.0, 3.0) if price and loan_term else None
    dp_50k = calculate_monthly(price, loan_term, 50000.0, 3.0) if price and loan_term else None

    # Depreciation
    depreciation = parse_price(raw.get("Depreciation", "").split(" ")[0], missing_fields, "Depreciation")

    # Road tax
    road_tax = parse_price(raw.get("Road Tax", "").split(" ")[0], missing_fields, "Road Tax")

    # Image URLs
    image_urls = []

    for img in soup.find_all("img", class_="carousel_image"):
        src = img.get("src")
        if not src:
            continue

        image_urls.append(src)

    # Deduplicate while preserving order
    image_urls = list(dict.fromkeys(image_urls))

    # Build model name with fallbacks (near the end, before return)
    model = build_model_name(raw, manufactured_year, url, missing_fields)

    return CarListing(
        model=model,
        price=price,
        end_coe_rebates=end_rebate,
        depreciation=depreciation,
        road_tax=road_tax,
        type=car_type,
        reg_date=reg_date_str,
        coe_left=coe_left_str,
        loan_term_months=loan_term,
        zero_dp_monthly=zero_dp,
        tenk_dp_monthly=dp_10k,
        twentyk_dp_monthly=dp_20k,
        thirtyk_dp_monthly=dp_30k,
        fortyk_dp_monthly=dp_40k,
        fiftyk_dp_monthly=dp_50k,
        mileage=parse_mileage(raw.get("Mileage", ""), missing_fields),
        no_owners=raw.get("No. of Owners"),
        curb_weight_kg=curb_weight,
        engine_cc=engine_cc,
        power_bhp=power_bhp,
        power_kw=power_kw,
        power_to_weight=power_to_weight,
        transmission=raw.get("Transmission"),
        vehicle_type=raw.get("Type of Vehicle"),
        coe=parse_price(raw.get("COE", ""), missing_fields, "COE"),
        arf=arf,
        omv=parse_price(raw.get("OMV", ""), missing_fields, "OMV"),
        url=url,
        photos=image_urls,
        missing_fields=missing_fields,
    )