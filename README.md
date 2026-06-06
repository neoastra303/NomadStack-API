# NomadStack API & Dashboard

NomadStack is a full-stack "Travel Intelligence" platform that aggregates real-time weather, economic, and tourism data to provide users with a unified "Travel Score" and actionable recommendations.

## 🏛️ Architecture Overview
*   **Backend:** FastAPI (Python) - High-performance asynchronous API.
*   **Frontend:** React (JavaScript) - Interactive, animated dashboard.
*   **Data Layer:** PostgreSQL (User data), Redis (Caching).
*   **Infrastructure:** Dockerized for consistent development and production environments.

## 🚀 Key Features
- **Intelligent Scoring:** Proprietary algorithm calculating city visitability.
- **Data Aggregation:** Real-time integration with WeatherAPI, ExchangeRateAPI, and OpenTripMap.
- **Production-Ready:** Includes Pydantic validation, error handling, and structured configuration.

## 🛠️ Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Node.js & npm
- Python 3.10+

### 1. Backend Setup
```bash
cd NomadStack-API
# Configure environment variables
cp .env.example .env
# Spin up infrastructure
docker-compose up -d
# Install dependencies
pip install -r requirements.txt
# Run API
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd nomadstack-web
npm install
npm run dev
```

## 🔐 Security & Production Practices
- **Environment Management:** All API keys and credentials are handled via `.env` (never committed).
- **Validation:** Strict data validation using Pydantic.
- **Error Handling:** Graceful degradation for external service failures.
- **Containerization:** Decoupled database and caching layers via Docker.

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
