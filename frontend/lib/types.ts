export type UserRole = "free" | "premium";

export interface ScrapeRequest {
  urls: string[];
  userrole: UserRole;
}

export interface CarListing {
    model: string;
    url: string;
  
    price: number | null;
    end_coe_rebates: number | null;
    depreciation: number | null;
    road_tax: number | null;
  
    type: string | null;
    reg_date: string | null;
    coe_left: string | null;
    loan_term_months: number | null;
  
    zero_dp_monthly: number | null;
    tenk_dp_monthly: number | null;
    twentyk_dp_monthly: number | null;
    thirtyk_dp_monthly: number | null;
    fortyk_dp_monthly: number | null;
    fiftyk_dp_monthly: number | null;
  
    mileage: number | null;
    no_owners: string | null;
  
    curb_weight_kg: number | null;
    engine_cc: number | null;
  
    power_bhp: number | null;
    power_kw: number | null;
    power_to_weight: number | null;
  
    transmission: string | null;
    vehicle_type: string | null;
  
    coe: number | null;
    arf: number | null;
    omv: number | null;
  
    photos: string[];
    missing_fields: string[];
  }
  

export interface ApiError {
  error: string;
  message: string;
  request_id?: string;
}