from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.models import User
from app.schemas.schemas import TokenResponse, UserCreate, UserLogin, UserProfile

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict) -> str:
    to_encode = {k: str(v) if k == "sub" else v for k, v in data.items()}
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post(
    "/register",
    response_model=TokenResponse,
    summary="Create a new account",
    description="Register a new user with username, email, and password. Returns a JWT token.",
    response_description="JWT access token with user profile",
)
async def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=pwd_context.hash(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id})
    return TokenResponse(
        access_token=token,
        user=UserProfile.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Sign in to your account",
    description="Authenticate with username and password. Returns a JWT token.",
    response_description="JWT access token with user profile",
)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.id})
    return TokenResponse(
        access_token=token,
        user=UserProfile.model_validate(user),
    )


@router.get(
    "/profile",
    response_model=UserProfile,
    summary="Get your profile",
    description="Returns the authenticated user's profile. Requires a Bearer token.",
    response_description="User profile with id, username, email",
)
async def profile(
    authorization: str = Header("", alias="Authorization"),
    db: Session = Depends(get_db),
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization[7:]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile.model_validate(user)
