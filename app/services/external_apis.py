import httpx

from app.core.config import get_settings
from app.core.exceptions import CityNotFoundError, ServiceUnavailableError
from app.schemas.schemas import ExchangeResponse, WeatherResponse
from app.services.cache import cache

settings = get_settings()

WEATHER_CACHE_TTL = 300
EXCHANGE_CACHE_TTL = 3600


class WeatherService:
    @staticmethod
    async def get_weather_data(city: str, client: httpx.AsyncClient) -> WeatherResponse:
        cache_key = f"weather:{city.lower()}"
        cached = await cache.get(cache_key)
        if cached:
            return WeatherResponse(**cached)

        url = f"http://api.weatherapi.com/v1/current.json?key={settings.WEATHER_API_KEY}&q={city}&aqi=no"
        try:
            response = await client.get(url)
        except httpx.RequestError as e:
            raise ServiceUnavailableError("Weather Service") from e

        if response.status_code == 400:
            raise CityNotFoundError(city)
        if response.status_code != 200:
            raise ServiceUnavailableError("Weather Service")

        data = response.json()
        result = WeatherResponse(
            temp_c=data["current"]["temp_c"],
            condition=data["current"]["condition"]["text"],
            humidity=data["current"]["humidity"],
            wind_kph=data["current"]["wind_kph"],
            is_day=data["current"]["is_day"],
        )
        await cache.set(cache_key, result.model_dump(), WEATHER_CACHE_TTL)
        return result


class ExchangeService:
    @staticmethod
    async def get_exchange_rate(
        client: httpx.AsyncClient,
        base_currency: str = "USD",
        target_currency: str = "EUR",
    ) -> ExchangeResponse:
        cache_key = f"exchange:{base_currency}:{target_currency}"
        cached = await cache.get(cache_key)
        if cached:
            return ExchangeResponse(**cached)

        url = f"https://v6.exchangerate-api.com/v6/{settings.EXCHANGE_RATE_API_KEY}/pair/{base_currency}/{target_currency}"
        try:
            response = await client.get(url)
        except httpx.RequestError as e:
            raise ServiceUnavailableError("Exchange Service") from e

        if response.status_code != 200:
            raise ServiceUnavailableError("Exchange Service")

        data = response.json()
        result = ExchangeResponse(
            base=base_currency,
            target=target_currency,
            rate=data["conversion_rate"],
        )
        await cache.set(cache_key, result.model_dump(), EXCHANGE_CACHE_TTL)
        return result
