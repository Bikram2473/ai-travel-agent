from typing import TypedDict, Optional

class TripState(TypedDict):
    origin: str
    destination: str
    dates: str
    duration_days: int
    budget: float
    hotel_tier: Optional[str]                           # NEW: AI chooses 'budget', 'standard', or 'luxury'
    current_itinerary: Optional[str]
    flight_cost: Optional[float]
    hotel_cost: Optional[float]
    total_cost: Optional[float]
    weather_forecast: Optional[str]                     # NEW: Added weather state
    iterations: int
    status: str
    log_history: str