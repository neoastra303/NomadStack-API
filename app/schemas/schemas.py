from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WeatherResponse(BaseModel):
    temp_c: float
    condition: str
    humidity: int
    wind_kph: float
    is_day: int


class ForecastDay(BaseModel):
    date: str
    max_temp_c: float
    min_temp_c: float
    condition: str
    chance_of_rain: int


class ForecastResponse(BaseModel):
    city: str
    days: list[ForecastDay]


class ExchangeResponse(BaseModel):
    base: str
    target: str
    rate: float


class AttractionResponse(BaseModel):
    name: str
    kinds: str
    lat: float
    lon: float
    distance: float | None = None


class CountryInfo(BaseModel):
    name: str
    capital: str
    region: str
    population: int
    flag: str
    languages: list[str]
    currencies: list[str]
    timezones: list[str]


class ScoreBreakdown(BaseModel):
    total: float = Field(..., ge=0, le=100)
    temperature_score: float = Field(..., ge=0, le=100)
    humidity_score: float = Field(..., ge=0, le=100)
    temperature_weight: float = 0.7
    humidity_weight: float = 0.3


class CityResult(BaseModel):
    city: str
    travel_score: float
    weather: WeatherResponse
    exchange: ExchangeResponse
    recommendation: str
    score_breakdown: ScoreBreakdown


class MultiCityResponse(BaseModel):
    results: list[CityResult]
    sorted_by: str = "score"


class TravelScoreResponse(BaseModel):
    city: str
    travel_score: float = Field(..., ge=0, le=100)
    weather: WeatherResponse
    forecast: list[ForecastDay] | None = None
    exchange: ExchangeResponse
    attractions: list[AttractionResponse] | None = None
    country_info: CountryInfo | None = None
    score_breakdown: ScoreBreakdown
    recommendation: str


class SearchHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    city_name: str
    travel_score: float
    timestamp: datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105
    user: UserProfile


class FavoriteCreate(BaseModel):
    city_name: str
    country: str | None = None
    lat: float | None = None
    lon: float | None = None


class FavoriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    city_name: str
    country: str | None = None
    lat: float | None = None
    lon: float | None = None
    created_at: datetime
