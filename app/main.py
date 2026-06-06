from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import search

app = FastAPI(
    title="NomadStack API",
    description="A Travel Intelligence API aggregating multiple data sources.",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/v1", tags=["Travel Intelligence"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to NomadStack API",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
