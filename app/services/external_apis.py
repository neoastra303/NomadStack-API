import httpx

from app.core.config import get_settings
from app.core.exceptions import CityNotFoundError, ServiceUnavailableError
from app.schemas.schemas import (
    AttractionResponse,
    CountryInfo,
    ExchangeResponse,
    ForecastDay,
    WeatherResponse,
)
from app.services.cache import cache

settings = get_settings()

WEATHER_CACHE_TTL = 300
EXCHANGE_CACHE_TTL = 3600
FORECAST_CACHE_TTL = 1800
ATTRACTIONS_CACHE_TTL = 86400
COUNTRY_CACHE_TTL = 86400


class WeatherService:
    @staticmethod
    async def get_weather_data(
        city: str,
        client: httpx.AsyncClient,
        api_key: str | None = None,
    ) -> WeatherResponse:
        cache_key = f"weather:{city.lower()}"
        cached = await cache.get(cache_key)
        if cached:
            return WeatherResponse(**cached)

        key = api_key or settings.WEATHER_API_KEY
        url = f"http://api.weatherapi.com/v1/current.json?key={key}&q={city}&aqi=no"
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

    @staticmethod
    async def get_forecast(
        city: str,
        client: httpx.AsyncClient,
        api_key: str | None = None,
        days: int = 7,
    ) -> list[ForecastDay]:
        cache_key = f"forecast:{city.lower()}:{days}"
        cached = await cache.get(cache_key)
        if cached:
            return [ForecastDay(**d) for d in cached]

        key = api_key or settings.WEATHER_API_KEY
        url = f"http://api.weatherapi.com/v1/forecast.json?key={key}&q={city}&days={days}&aqi=no"
        try:
            response = await client.get(url)
        except httpx.RequestError as e:
            raise ServiceUnavailableError("Weather Service") from e

        if response.status_code == 400:
            raise CityNotFoundError(city)
        if response.status_code != 200:
            raise ServiceUnavailableError("Weather Service")

        data = response.json()
        result = [
            ForecastDay(
                date=d["date"],
                max_temp_c=d["day"]["maxtemp_c"],
                min_temp_c=d["day"]["mintemp_c"],
                condition=d["day"]["condition"]["text"],
                chance_of_rain=d["day"]["daily_chance_of_rain"],
            )
            for d in data["forecast"]["forecastday"]
        ]
        await cache.set(cache_key, [r.model_dump() for r in result], FORECAST_CACHE_TTL)
        return result


class ExchangeService:
    @staticmethod
    async def get_exchange_rate(
        client: httpx.AsyncClient,
        base_currency: str = "USD",
        target_currency: str = "EUR",
        api_key: str | None = None,
    ) -> ExchangeResponse:
        cache_key = f"exchange:{base_currency}:{target_currency}"
        cached = await cache.get(cache_key)
        if cached:
            return ExchangeResponse(**cached)

        key = api_key or settings.EXCHANGE_RATE_API_KEY
        url = f"https://v6.exchangerate-api.com/v6/{key}/pair/{base_currency}/{target_currency}"
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


class TripService:
    @staticmethod
    async def get_attractions(
        city: str,
        client: httpx.AsyncClient,
        lat: float | None = None,
        lon: float | None = None,
        radius: int = 5000,
        limit: int = 10,
    ) -> list[AttractionResponse]:
        cache_key = f"attractions:{city.lower()}:{limit}"
        cached = await cache.get(cache_key)
        if cached:
            return [AttractionResponse(**a) for a in cached]

        if not settings.OPEN_TRIP_MAP_KEY:
            return []

        url = (
            f"https://api.opentripmap.com/0.1/en/places/radius"
            f"?radius={radius}&lon={lon}&lat={lat}"
            f"&rate=2&format=json&limit={limit}"
            f"&apikey={settings.OPEN_TRIP_MAP_KEY}"
        )
        try:
            response = await client.get(url)
        except httpx.RequestError:
            return []

        if response.status_code != 200:
            return []

        data = response.json()
        result = [
            AttractionResponse(
                name=p.get("name", "Unknown"),
                kinds=p.get("kinds", ""),
                lat=float(p.get("point", {}).get("lat", 0)),
                lon=float(p.get("point", {}).get("lon", 0)),
                distance=p.get("dist"),
            )
            for p in data if p.get("name")
        ][:limit]
        await cache.set(cache_key, [r.model_dump() for r in result], ATTRACTIONS_CACHE_TTL)
        return result

    @staticmethod
    async def get_country_info(
        country_name: str,
        client: httpx.AsyncClient,
    ) -> CountryInfo | None:
        cache_key = f"country:{country_name.lower().replace(' ', '_')}"
        cached = await cache.get(cache_key)
        if cached:
            return CountryInfo(**cached)

        url = f"https://restcountries.com/v3.1/name/{country_name}"
        try:
            response = await client.get(url)
        except httpx.RequestError:
            return None

        if response.status_code != 200:
            return None

        data = response.json()
        if not data:
            return None

        c = data[0]
        langs = list(c.get("languages", {}).values()) if c.get("languages") else []
        currencies = list(c.get("currencies", {}).keys()) if c.get("currencies") else []
        timezones = c.get("timezones", [])
        flag = c.get("flags", {}).get("svg", "")
        capital = c.get("capital", [""])[0] if c.get("capital") else ""

        result = CountryInfo(
            name=c.get("name", {}).get("common", country_name),
            capital=capital,
            region=c.get("region", ""),
            population=c.get("population", 0),
            flag=flag,
            languages=langs,
            currencies=currencies,
            timezones=timezones,
        )
        await cache.set(cache_key, result.model_dump(), COUNTRY_CACHE_TTL)
        return result
