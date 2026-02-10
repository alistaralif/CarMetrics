from pydantic import BaseModel, Field
from typing import Optional, List


class CarListing(BaseModel):
    model: str
    url: str
    photos: List[str] = []

    price: Optional[float] = None
    depreciation: Optional[float] = None
    road_tax: Optional[float] = None

    type: Optional[str] = None
    reg_date: Optional[str] = None
    coe_left: Optional[str] = None
    loan_term_months: Optional[int] = None

    zero_dp_monthly: Optional[float] = None
    tenk_dp_monthly: Optional[float] = None
    twentyk_dp_monthly: Optional[float] = None
    thirtyk_dp_monthly: Optional[float] = None
    fortyk_dp_monthly: Optional[float] = None
    fiftyk_dp_monthly: Optional[float] = None

    mileage: Optional[int] = None
    no_owners: Optional[str] = None

    curb_weight_kg: Optional[float] = None
    engine_cc: Optional[int] = None

    power_bhp: Optional[int] = None
    power_kw: Optional[float] = None
    power_to_weight: Optional[float] = None

    transmission: Optional[str] = None
    vehicle_type: Optional[str] = None

    coe: Optional[float] = None
    arf: Optional[float] = None
    omv: Optional[float] = None

    end_coe_rebates: Optional[float] = None

    missing_fields: list[str] = []
