# NomadStack API

> Travel Intelligence API — aggregates real-time weather, exchange rate, and tourism data into a unified **Travel Score** with actionable recommendations.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=fff)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=fff)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Features

- **Intelligent Scoring** — proprietary algorithm that rates city visitability based on weather comfort
- **Multi-source Aggregation** — real-time data from WeatherAPI, ExchangeRate-API, and OpenTripMap
- **Async-First** — built on `asyncio` with `httpx.AsyncClient` connection pooling for concurrent external API calls
- **Redis Caching** — 5-minute weather cache / 1-hour exchange rate cache with automatic fallback when Redis is unavailable
- **Structured Logging** — `structlog` with ISO timestamps, context-aware loggers
- **Domain Exceptions** — typed error hierarchy (`CityNotFoundError`, `ServiceUnavailableError`) mapped to proper HTTP status codes (404, 502)
- **DB Migrations** — Alembic-managed schema for users, search history, and favorites
- **Pydantic V2** — strict validation with `ConfigDict`, `Field` constraints, and ORM mode
- **Dockerized** — PostgreSQL 16 + Redis 7 via Compose, ready-to-deploy Dockerfile

---

## Quick Start

```bash
# Clone
git clone https://github.com/neoastra303/NomadStack-API.git
cd NomadStack-API

# Configure
cp .env.example .env
# Edit .env — add your API keys (WEATHER_API_KEY, EXCHANGE_RATE_API_KEY)

# Start infrastructure
docker compose up -d

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger UI.

---

## Project Structure

```
NomadStack-API/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── search.py          # /api/v1/search endpoint
│   ├── core/
│   │   ├── config.py              # Pydantic-settings (env-based)
│   │   ├── database.py            # SQLAlchemy engine + session
│   │   └── exceptions.py          # Domain exception hierarchy
│   ├── models/
│   │   └── models.py              # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── schemas.py             # Pydantic V2 request/response models
│   ├── services/
│   │   ├── cache.py               # Async Redis caching layer
│   │   └── external_apis.py       # WeatherAPI + ExchangeRate-API clients
│   └── main.py                    # FastAPI app, lifespan, exception handlers
├── alembic/                       # Database migrations
├── tests/                         # pytest suite (11 tests)
├── docker-compose.yml             # PostgreSQL + Redis
├── Dockerfile                     # Production container
├── .env.example                   # Environment variable template
├── pyproject.toml                 # Modern Python packaging
└── requirements.txt               # Pin-to-build dependencies
```

---

## API

### `GET /api/v1/search`

Query travel intelligence for a city.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `city` | `string` | — | City name (min 2 chars) |
| `currency` | `string` | `EUR` | Target currency for exchange rate |

**Example:**

```bash
curl "http://localhost:8000/api/v1/search?city=Paris&currency=JPY"
```

**Response:**

```json
{
  "city": "Paris",
  "travel_score": 78.5,
  "weather": {
    "temp_c": 22.0,
    "condition": "Partly cloudy",
    "humidity": 55,
    "wind_kph": 12.0,
    "is_day": 1
  },
  "exchange": {
    "base": "USD",
    "target": "JPY",
    "rate": 149.82
  },
  "recommendation": "Great time to visit!"
}
```

### Other Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Welcome message with docs link |
| `GET /health` | Health check (returns `{"status": "healthy"}`) |

---

## Configuration

All configuration lives in `.env`:

```ini
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nomadstack

# Redis (optional — caching falls back gracefully)
REDIS_URL=redis://localhost:6379/0

# External API keys
WEATHER_API_KEY=your_key
EXCHANGE_RATE_API_KEY=your_key
OPEN_TRIP_MAP_KEY=your_key

# Security (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Testing

```bash
pytest -v
```

11 tests covering scoring algorithm, domain exceptions, and Pydantic schema validation.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI 0.111 |
| **Runtime** | Python 3.11+ / Uvicorn |
| **ORM** | SQLAlchemy 2.0 |
| **Validation** | Pydantic V2 |
| **Cache** | Redis 7 (via `redis.asyncio`) |
| **HTTP Client** | httpx 0.27 (connection-pooled) |
| **Migrations** | Alembic |
| **Logging** | structlog |
| **Database** | PostgreSQL 16 |
| **Testing** | pytest + pytest-asyncio |
| **Container** | Docker / Compose |

---

## License

MIT — see [LICENSE](LICENSE).
