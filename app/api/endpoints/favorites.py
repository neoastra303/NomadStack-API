from fastapi import APIRouter, Depends, HTTPException, Query
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


@router.get("/favorites", response_model=list[FavoriteResponse])
async def list_favorites(
    authorization: str = "",
    db: Session = Depends(get_db),
):
    user = _get_user(authorization, db)
    return db.query(Favorite).filter(Favorite.user_id == user.id).order_by(Favorite.created_at.desc()).all()


@router.post("/favorites", response_model=FavoriteResponse)
async def add_favorite(
    data: FavoriteCreate,
    authorization: str = "",
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


@router.delete("/favorites/{city}")
async def remove_favorite(
    city: str,
    authorization: str = "",
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


@router.get("/history", response_model=list[SearchHistorySchema])
async def list_history(
    authorization: str = "",
    limit: int = Query(20, ge=1, le=100),
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
