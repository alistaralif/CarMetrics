import re
# from app.utils.finance import (
#     calculate_car_age_months,
#     calculate_loan_term,
#     calculate_monthly,
# )


NA_VALUES = {"N.A.", "N.A", "Missing", "-"}


def parse_price(value: str, missing: list, field: str):
    if not value or value in NA_VALUES:
        missing.append(field)
        return None
    try:
        return float(value.replace("$", "").replace(",", ""))
    except ValueError:
        missing.append(f"{field} (invalid)")
        return None


def parse_int(value: str, missing: list, field: str):
    if not value or value in NA_VALUES:
        missing.append(field)
        return None
    try:
        return int(value.split(" ")[0].replace(",", ""))
    except ValueError:
        missing.append(f"{field} (invalid)")
        return None


def parse_float(value: str, missing: list, field: str):
    if not value or value in NA_VALUES:
        missing.append(field)
        return None
    try:
        return float(value.split(" ")[0].replace(",", ""))
    except ValueError:
        missing.append(f"{field} (invalid)")
        return None


def parse_mileage(value: str, missing: list):
    if not value or value in NA_VALUES:
        missing.append("Mileage")
        return None

    match = re.search(r"([\d,]+)\s*km", value)
    if match:
        return int(match.group(1).replace(",", ""))

    missing.append("Mileage (invalid)")
    return None