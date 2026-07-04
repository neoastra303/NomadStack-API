from app.schemas.schemas import TravelScoreResponse, WeatherResponse, ExchangeResponse


def test_weather_response():
    w = WeatherResponse(temp_c=25.0, condition="Sunny", humidity=50, wind_kph=10.0, is_day=1)
    assert w.temp_c == 25.0


def test_exchange_response():
    e = ExchangeResponse(base="USD", target="EUR", rate=0.92)
    assert e.rate == 0.92


def test_travel_score_response():
    w = WeatherResponse(temp_c=25.0, condition="Sunny", humidity=50, wind_kph=10.0, is_day=1)
    e = ExchangeResponse(base="USD", target="EUR", rate=0.92)
    t = TravelScoreResponse(city="Paris", travel_score=85.0, weather=w, exchange=e, recommendation="Great!")
    assert t.travel_score == 85.0
    assert t.city == "Paris"
    assert t.weather.condition == "Sunny"


def test_travel_score_validation():
    w = WeatherResponse(temp_c=25.0, condition="Sunny", humidity=50, wind_kph=10.0, is_day=1)
    e = ExchangeResponse(base="USD", target="EUR", rate=0.92)
    try:
        TravelScoreResponse(city="Test", travel_score=150, weather=w, exchange=e, recommendation="")
        assert False, "Should have raised validation error"
    except Exception:
        pass
