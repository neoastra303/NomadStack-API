from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class WeatherResponse(BaseModel):
    temp_c: float
    condition: str
    humidity: int
    wind_kph: float
    is_day: int

class ExchangeResponse(BaseModel):
    base: str
    target: str
    rate: float

class TravelScoreResponse(BaseModel):
    city: str
    travel_score: float = Field(..., ge=0, le=100)
    weather: WeatherResponse
    exchange: ExchangeResponse
    recommendation: str

class SearchHistorySchema(BaseModel):
    id: int
    city_name: str
    travel_score: float
    timestamp: datetime

    class Config:
        from_attributes = True
