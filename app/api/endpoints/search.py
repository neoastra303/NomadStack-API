from fastapi import APIRouter, Depends, Query
from app.services.external_apis import WeatherService, ExchangeService
from app.schemas.schemas import TravelScoreResponse
import math

router = APIRouter()

def calculate_score(temp_c: float, humidity: int) -> float:
    # A simple mock logic for the Travel Score
    # Ideal temp: 20-25C, Low humidity
    temp_score = max(0, 100 - abs(temp_c - 22) * 4)
    hum_score = 100 - humidity
    return round((temp_score * 0.7) + (hum_score * 0.3), 1)

@router.get("/search", response_model=TravelScoreResponse)
async def search_city(
    city: str = Query(..., min_length=2, description="The name of the city to search for"),
    currency: str = Query("EUR", description="Target currency for exchange rate")
):
    # Fetch Data in Parallel
    import asyncio
    weather_task = WeatherService.get_weather_data(city)
    exchange_task = ExchangeService.get_exchange_rate("USD", currency)
    
    weather, exchange = await asyncio.gather(weather_task, exchange_task)
    
    score = calculate_score(weather["temp_c"], weather["humidity"])
    
    # Simple Recommendation Logic
    recommendation = "Great time to visit!" if score > 75 else "Maybe check another city or season."
    if weather["temp_c"] > 35: recommendation = "It's too hot for comfortable travel."
    if weather["temp_c"] < 5: recommendation = "Pack heavy winter clothes!"

    return {
        "city": city.capitalize(),
        "travel_score": score,
        "weather": weather,
        "exchange": exchange,
        "recommendation": recommendation
    }
