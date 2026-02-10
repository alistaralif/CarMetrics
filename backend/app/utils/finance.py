import math
from datetime import datetime


def calculate_car_age_months(date_str: str) -> int | None:
    """
    Calculates the age of a car in months from a registration date string.
    Expected format: DD-Mon-YYYY (e.g. 15-Feb-2019)
    """
    try:
        reg_date = datetime.strptime(date_str, "%d-%b-%Y")
    except ValueError:
        return None

    today = datetime.now()
    return (today.year - reg_date.year) * 12 + (today.month - reg_date.month)


def calculate_loan_term(coe_left_months: int, buffer_months: int = 4) -> int:
    """
    Calculates usable loan term after subtracting buffer months.
    """
    if coe_left_months <= buffer_months:
        return 0
    return coe_left_months - buffer_months


def calculate_monthly(
    price: float,
    loan_term: int,
    downpayment: float = 0.0,
    interest_rate: float = 4.98,
) -> float:
    """
    Calculates estimated monthly car loan instalment using simple interest.
    """
    loan_amount = price - downpayment

    if loan_amount <= 0 or loan_term <= 0:
        return 0.0

    no_of_years = math.ceil(loan_term / 12)
    total_interest_multiplier = 1 + (interest_rate / 100) * no_of_years

    monthly = (loan_amount * total_interest_multiplier) / loan_term
    return round(monthly, 2)
