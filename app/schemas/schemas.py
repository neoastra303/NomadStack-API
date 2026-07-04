from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    city_name: str
    travel_score: float
    timestamp: datetime
