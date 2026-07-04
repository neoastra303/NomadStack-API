from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow():
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    searches = relationship("SearchHistory", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    city_name = Column(String, nullable=False)
    country = Column(String)
    travel_score = Column(Float)
    timestamp = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="searches")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    city_name = Column(String, nullable=False)
    country = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="favorites")
