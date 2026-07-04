from fastapi import APIRouter, Depends, Header, HTTPException, Query
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.models import Favorite, SearchHistory, User
from app.schemas.schemas import FavoriteCreate, FavoriteResponse, SearchHistorySchema

router = APIRouter(prefix="/me", tags=["User"])
settings = get_settings()


def _get_user(token: str, db: Session) -> User:
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    try:
        payload = jwt.decode(token[7:], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get(
    "/favorites",
    response_model=list[FavoriteResponse],
    summary="List favorite cities",
    description="Returns all saved favorite cities for the authenticated user.",
    response_description="List of favorite cities with metadata",
)
async def list_favorites(
    authorization: str = Header("", alias="Authorization"),
    db: Session = Depends(get_db),
):
    user = _get_user(authorization, db)
    return (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )


@router.post(
    "/favorites",
    response_model=FavoriteResponse,
    summary="Add a favorite city",
    description="Save a city to the authenticated user's favorites list.",
    response_description="The created favorite entry",
)
async def add_favorite(
    data: FavoriteCreate,
    authorization: str = Header("", alias="Authorization"),
    db: Session = Depends(get_db),
):
    user = _get_user(authorization, db)
    existing = db.query(Favorite).filter(
        Favorite.user_id == user.id,
        Favorite.city_name == data.city_name,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="City already in favorites")

    fav = Favorite(user_id=user.id, **data.model_dump())
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return FavoriteResponse.model_validate(fav)


@router.delete(
    "/favorites/{city}",
    summary="Remove a favorite city",
    description="Remove a city from the authenticated user's favorites.",
    response_description="Confirmation of removal",
)
async def remove_favorite(
    city: str,
    authorization: str = Header("", alias="Authorization"),
    db: Session = Depends(get_db),
):
    user = _get_user(authorization, db)
    fav = db.query(Favorite).filter(
        Favorite.user_id == user.id,
        Favorite.city_name == city,
    ).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(fav)
    db.commit()
    return {"status": "removed", "city": city}


@router.get(
    "/history",
    response_model=list[SearchHistorySchema],
    summary="Get search history",
    description="Returns the authenticated user's recent search history.",
    response_description="List of past searches with timestamps",
)
async def list_history(
    authorization: str = Header("", alias="Authorization"),
    limit: int = Query(20, ge=1, le=100, description="Number of history entries to return"),
    db: Session = Depends(get_db),
):
    user = _get_user(authorization, db)
    return (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == user.id)
        .order_by(SearchHistory.timestamp.desc())
        .limit(limit)
        .all()
    )
