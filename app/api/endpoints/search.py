import asyncio
from typing import Any

import httpx
from fastapi import APIRouter, Header, Query, Request

from app.schemas.schemas import (
    CityResult,
    ForecastResponse,
    MultiCityResponse,
    ScoreBreakdown,
    TravelScoreResponse,
)
from app.services.external_apis import ExchangeService, TripService, WeatherService

router = APIRouter()


def calculate_score(temp_c: float, humidity: int) -> ScoreBreakdown:
    temp_score = max(0, 100 - abs(temp_c - 22) * 4)
    hum_score = 100 - humidity
    total = round((temp_score * 0.7) + (hum_score * 0.3), 1)
    return ScoreBreakdown(
        total=total,
        temperature_score=round(temp_score, 1),
        humidity_score=max(0, round(hum_score, 1)),
    )


def make_recommendation(score: float, temp_c: float) -> str:
    if temp_c > 35:
        return "It's too hot for comfortable travel."
    if temp_c < 5:
        return "Pack heavy winter clothes!"
    if score > 75:
        return "Great time to visit!"
    return "Maybe check another city or season."


async def _search_single(
    city: str,
    currency: str,
    client: httpx.AsyncClient,
    weather_key: str | None,
    exchange_key: str | None,
    include_extra: bool = False,
) -> CityResult:
    weather_task = WeatherService.get_weather_data(city, client, api_key=weather_key)
    exchange_task = ExchangeService.get_exchange_rate(client, "USD", currency, api_key=exchange_key)

    if include_extra:
        forecast_task = WeatherService.get_forecast(city, client, api_key=weather_key)
        weather, exchange, _ = await asyncio.gather(weather_task, exchange_task, forecast_task)
    else:
        weather, exchange = await asyncio.gather(weather_task, exchange_task)

    breakdown = calculate_score(weather.temp_c, weather.humidity)
    recommendation = make_recommendation(breakdown.total, weather.temp_c)

    return CityResult(
        city=city.title(),
        travel_score=breakdown.total,
        weather=weather,
        exchange=exchange,
        recommendation=recommendation,
        score_breakdown=breakdown,
    )


@router.get(
    "/search",
    response_model=TravelScoreResponse,
    summary="Get travel score for a city",
    description="Returns a travel score (0-100) for a city based on weather and exchange rate. "
    "Optionally include 7-day forecast, nearby attractions, and country information.",
    response_description="Travel score with weather, exchange rate, and optional extras",
)
async def search_city(
    request: Request,
    city: str = Query(
        ..., min_length=2,
        description="City name to search for",
        examples=["Paris", "London", "Tokyo"],
    ),
    currency: str = Query(
        "EUR",
        description="Target currency for exchange rate (USD base)",
        examples=["EUR", "GBP", "JPY"],
    ),
    include: str = Query(
        "",
        description="Comma-separated extras: forecast, attractions, country",
        examples=["forecast,attractions,country"],
    ),
    x_weather_key: str | None = Header(None, alias="X-Weather-Api-Key"),
    x_exchange_key: str | None = Header(None, alias="X-Exchange-Api-Key"),
):
    client = request.app.state.http_client
    extras = {e.strip() for e in include.split(",") if e.strip()}

    weather_task = WeatherService.get_weather_data(city, client, api_key=x_weather_key)
    exchange_task = ExchangeService.get_exchange_rate(
        client, "USD", currency, api_key=x_exchange_key
    )
    tasks: list[Any] = [weather_task, exchange_task]

    if "forecast" in extras:
        tasks.append(WeatherService.get_forecast(city, client, api_key=x_weather_key))
        results = await asyncio.gather(*tasks)
        weather, exchange, forecast = results[0], results[1], results[2]
    else:
        weather, exchange = await asyncio.gather(*tasks)
        forecast = None

    breakdown = calculate_score(weather.temp_c, weather.humidity)
    recommendation = make_recommendation(breakdown.total, weather.temp_c)

    attractions = None
    country_info = None

    if "attractions" in extras:
        try:
            attractions = await TripService.get_attractions(city, client)
        except Exception:
            attractions = []

    if "country" in extras:
        try:
            country_info = await TripService.get_country_info(city, client)
        except Exception:
            country_info = None

    return TravelScoreResponse(
        city=city.title(),
        travel_score=breakdown.total,
        weather=weather,
        forecast=forecast,
        exchange=exchange,
        attractions=attractions,
        country_info=country_info,
        score_breakdown=breakdown,
        recommendation=recommendation,
    )


@router.get(
    "/compare",
    response_model=MultiCityResponse,
    summary="Compare multiple cities",
    description="Compare travel scores across multiple cities, ranked from best to worst.",
    response_description="Ranked list of city travel scores",
)
async def compare_cities(
    request: Request,
    cities: str = Query(
        ...,
        description="Comma-separated city names to compare",
        examples=["Paris, London, Tokyo"],
    ),
    currency: str = Query("EUR", description="Target currency"),
    x_weather_key: str | None = Header(None, alias="X-Weather-Api-Key"),
    x_exchange_key: str | None = Header(None, alias="X-Exchange-Api-Key"),
):
    client = request.app.state.http_client
    city_list = [c.strip() for c in cities.split(",") if c.strip()]

    tasks = [
        _search_single(c, currency, client, x_weather_key, x_exchange_key)
        for c in city_list
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    valid: list[CityResult] = []
    for r in results:
        if not isinstance(r, Exception):
            valid.append(r)  # type: ignore[arg-type]

    valid.sort(key=lambda x: x.travel_score, reverse=True)
    return MultiCityResponse(results=valid)


@router.get(
    "/forecast",
    response_model=ForecastResponse,
    summary="Get 7-day forecast",
    description="Returns a multi-day weather forecast for a city.",
    response_description="Daily forecast with temperatures, conditions, and rain chance",
)
async def forecast(
    request: Request,
    city: str = Query(..., min_length=2, examples=["Paris"]),
    days: int = Query(7, ge=1, le=10, description="Number of forecast days"),
    x_weather_key: str | None = Header(None, alias="X-Weather-Api-Key"),
):
    client = request.app.state.http_client
    days_data = await WeatherService.get_forecast(city, client, api_key=x_weather_key, days=days)
    return ForecastResponse(city=city.title(), days=days_data)
