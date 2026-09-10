from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.dependencies import get_db, get_current_user
from app.models import User
from app import schemas
from app.core import security


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code= status.HTTP_201_CREATED, response_model= schemas.UserResponse)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user_existant = await db.execute(select(User).where(User.email == user.email))
    user_existant = user_existant.scalar_one_or_none()
    if user_existant is not None:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "email existant")
    mot_de_passe_hasher = security.hasher_mot_de_passe(user.mot_de_passe)
    new_user = User(
        nom = user.nom,
        email = user.email,
        mot_de_passe = mot_de_passe_hasher,
        role = "membre"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model= schemas.Token)
async def login(user: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user_existant = await db.execute(select(User).where(user.username == User.email))
    user_existant = user_existant.scalar_one_or_none()
    if user_existant is None:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "email incorrect")
    if not security.verifier_hash(user.password, user_existant.mot_de_passe):
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "mot de passe incorrect")
    tokenData = security.creer_access_token(data={
        "user_id": user_existant.id,
        "role": user_existant.role
    })
    token = schemas.Token(
        access_token= tokenData,
        token_type= "bearer"
    )
    return token