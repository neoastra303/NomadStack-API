import pytest
from pydantic import ValidationError

from app.schemas.schemas import (
    AttractionResponse,
    CountryInfo,
    ExchangeResponse,
    FavoriteCreate,
    ForecastDay,
    ScoreBreakdown,
    TravelScoreResponse,
    UserCreate,
    UserLogin,
    WeatherResponse,
)


def test_weather_response():
    w = WeatherResponse(temp_c=25.0, condition="Sunny", humidity=50, wind_kph=10.0, is_day=1)
    assert w.temp_c == 25.0


def test_exchange_response():
    e = ExchangeResponse(base="USD", target="EUR", rate=0.92)
    assert e.rate == 0.92


def test_forecast_day():
    f = ForecastDay(date="2025-01-01", max_temp_c=30.0, min_temp_c=20.0, condition="Clear", chance_of_rain=10)
    assert f.chance_of_rain == 10


def test_attraction_response():
    a = AttractionResponse(name="Eiffel Tower", kinds="cultural", lat=48.85, lon=2.29)
    assert a.name == "Eiffel Tower"


def test_country_info():
    c = CountryInfo(name="France", capital="Paris", region="Europe", population=67_000_000,
                    flag="🇫🇷", languages=["French"], currencies=["EUR"], timezones=["UTC+1"])
    assert c.capital == "Paris"


def test_travel_score_response_with_breakdown():
    w = WeatherResponse(temp_c=25.0, condition="Sunny", humidity=50, wind_kph=10.0, is_day=1)
    e = ExchangeResponse(base="USD", target="EUR", rate=0.92)
    b = ScoreBreakdown(total=85.0, temperature_score=80.0, humidity_score=70.0)
    t = TravelScoreResponse(city="Paris", travel_score=85.0, weather=w, exchange=e,
                            recommendation="Great!", score_breakdown=b)
    assert t.travel_score == 85.0
    assert t.score_breakdown.total == 85.0


def test_travel_score_with_extras():
    w = WeatherResponse(temp_c=25.0, condition="Sunny", humidity=50, wind_kph=10.0, is_day=1)
    e = ExchangeResponse(base="USD", target="EUR", rate=0.92)
    b = ScoreBreakdown(total=85.0, temperature_score=80.0, humidity_score=70.0)
    f = [ForecastDay(date="2025-01-01", max_temp_c=30.0, min_temp_c=20.0, condition="Clear", chance_of_rain=10)]
    a = [AttractionResponse(name="Eiffel Tower", kinds="cultural", lat=48.85, lon=2.29)]
    t = TravelScoreResponse(city="Paris", travel_score=85.0, weather=w, exchange=e,
                            recommendation="Great!", score_breakdown=b,
                            forecast=f, attractions=a)
    assert t.forecast[0].condition == "Clear"
    assert t.attractions[0].name == "Eiffel Tower"


def test_travel_score_validation():
    w = WeatherResponse(temp_c=25.0, condition="Sunny", humidity=50, wind_kph=10.0, is_day=1)
    e = ExchangeResponse(base="USD", target="EUR", rate=0.92)
    b = ScoreBreakdown(total=85.0, temperature_score=80.0, humidity_score=70.0)
    with pytest.raises(ValidationError):
        TravelScoreResponse(city="Test", travel_score=150, weather=w, exchange=e,
                            recommendation="", score_breakdown=b)


def test_user_create_valid():
    u = UserCreate(username="alice", email="alice@test.com", password="secret123")
    assert u.username == "alice"


def test_user_create_short_username():
    with pytest.raises(ValidationError):
        UserCreate(username="a", email="a@b.com", password="secret123")


def test_user_create_short_password():
    with pytest.raises(ValidationError):
        UserCreate(username="bob", email="bob@test.com", password="ab1")


def test_user_login():
    u = UserLogin(username="alice", password="secret123")
    assert u.username == "alice"


def test_favorite_create():
    f = FavoriteCreate(city_name="Paris", country="France")
    assert f.city_name == "Paris"


def test_favorite_create_with_coords():
    f = FavoriteCreate(city_name="London", lat=51.5, lon=-0.13)
    assert f.lat == 51.5
