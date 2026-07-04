import asyncio

from fastapi import APIRouter, Header, Query, Request

from app.schemas.schemas import TravelScoreResponse
from app.services.external_apis import ExchangeService, WeatherService

router = APIRouter()


def calculate_score(temp_c: float, humidity: int) -> float:
    temp_score = max(0, 100 - abs(temp_c - 22) * 4)
    hum_score = 100 - humidity
    return round((temp_score * 0.7) + (hum_score * 0.3), 1)


@router.get("/search", response_model=TravelScoreResponse)
async def search_city(
    request: Request,
    city: str = Query(..., min_length=2, description="The name of the city to search for"),
    currency: str = Query("EUR", description="Target currency for exchange rate"),
    x_weather_key: str | None = Header(None, alias="X-Weather-Api-Key"),
    x_exchange_key: str | None = Header(None, alias="X-Exchange-Api-Key"),
):
    client = request.app.state.http_client

    weather_task = WeatherService.get_weather_data(city, client, api_key=x_weather_key)
    exchange_task = ExchangeService.get_exchange_rate(client, "USD", currency, api_key=x_exchange_key)

    weather, exchange = await asyncio.gather(weather_task, exchange_task)

    score = calculate_score(weather.temp_c, weather.humidity)

    if weather.temp_c > 35:
        recommendation = "It's too hot for comfortable travel."
    elif weather.temp_c < 5:
        recommendation = "Pack heavy winter clothes!"
    elif score > 75:
        recommendation = "Great time to visit!"
    else:
        recommendation = "Maybe check another city or season."

    return TravelScoreResponse(
        city=city.title(),
        travel_score=score,
        weather=weather,
        exchange=exchange,
        recommendation=recommendation,
    )
