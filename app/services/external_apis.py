import httpx
from fastapi import HTTPException
from app.core.config import get_settings

settings = get_settings()

class WeatherService:
    @staticmethod
    async def get_weather_data(city: str):
        url = f"http://api.weatherapi.com/v1/current.json?key={settings.WEATHER_API_KEY}&q={city}&aqi=no"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "temp_c": data["current"]["temp_c"],
                        "condition": data["current"]["condition"]["text"],
                        "humidity": data["current"]["humidity"],
                        "wind_kph": data["current"]["wind_kph"],
                        "is_day": data["current"]["is_day"]
                    }
                elif response.status_code == 400:
                    raise HTTPException(status_code=400, detail="City not found or invalid request.")
                else:
                    # Log error here in real production
                    raise HTTPException(status_code=502, detail="External Weather Service is currently unavailable.")
            except httpx.RequestError:
                raise HTTPException(status_code=503, detail="Could not reach Weather Service.")

class ExchangeService:
    @staticmethod
    async def get_exchange_rate(base_currency: str = "USD", target_currency: str = "EUR"):
        url = f"https://v6.exchangerate-api.com/v6/{settings.EXCHANGE_RATE_API_KEY}/pair/{base_currency}/{target_currency}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "base": base_currency,
                        "target": target_currency,
                        "rate": data["conversion_rate"]
                    }
                else:
                    return {"error": "Could not fetch exchange rate", "rate": 1.0} # Graceful degradation
            except httpx.RequestError:
                return {"error": "Exchange service unreachable", "rate": 1.0}
