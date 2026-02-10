import re
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse

CURRENT_YEAR = datetime.now().year


def extract_model_from_url(url: str) -> str | None:
    """Extract model name from SGCarMart URL as fallback."""
    try:
        path = urlparse(url).path
        # URL format: /used-cars/info/toyota-yaris-cross-15a-1411501
        match = re.search(r"/info/([^/]+)-\d+$", path)
        if match:
            model_slug = match.group(1)
            return " ".join(
                word.upper() if len(word) <= 3 else word.title()
                for word in model_slug.split("-")
            )
    except Exception:
        pass
    return None


def extract_title(soup: BeautifulSoup) -> str | None:
    """Extract car title from the listing link."""
    
    # Primary: Find the link with styles_link_color__ class
    link = soup.find("a", class_=re.compile(r"styles_link_color__"))
    if link and link.text.strip():
        title = link.text.strip()
        # Remove COE info: "MINI Cooper S 1.6A Sunroof (COE till 04/2031)" -> "MINI Cooper S 1.6A Sunroof"
        title = re.sub(r"\s*\(COE\s+till\s+\d{2}/\d{4}\)", "", title, flags=re.IGNORECASE)
        return title.strip()
    
    return None


def extract_manufactured_year(raw: dict) -> int | None:
    """Extract manufactured year from raw data."""
    
    # Strategy 1: From Manufactured field
    manufactured = raw.get("Manufactured", "")
    if manufactured:
        match = re.search(r"(\d{4})", manufactured)
        if match:
            year = int(match.group(1))
            if 1980 <= year <= CURRENT_YEAR + 1:
                return year

    # Strategy 2: From Reg Date field
    reg_date = raw.get("Reg Date", "")
    if reg_date:
        match = re.search(r"(\d{4})", reg_date)
        if match:
            year = int(match.group(1))
            if 1980 <= year <= CURRENT_YEAR + 1:
                return year

    return None


def build_model_name(
    raw: dict, manufactured_year: int | None, url: str, missing_fields: list[str]
) -> str:
    """Build model name with cascading fallbacks."""
    title = raw.get("Title")
    year_str = str(manufactured_year) if manufactured_year else None

    if title and year_str:
        return f"{year_str} {title}"
    elif title:
        return title
    elif year_str:
        url_model = extract_model_from_url(url)
        return f"{year_str} {url_model}" if url_model else f"{year_str} (Unknown Model)"
    else:
        url_model = extract_model_from_url(url)
        if not url_model:
            missing_fields.append("Model")
        return url_model if url_model else "Unknown Model"