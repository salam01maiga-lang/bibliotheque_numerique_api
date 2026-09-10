from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.core.config import settings
from app.models import User
from app.core.security import verifier_access_token
from sqlalchemy.future import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl= "auth/login")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = verifier_access_token(token)
    if payload is None:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "token invalide")
    user_id = payload.get("user_id")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Utilisateur introuvable")
    return user

async def require_admin(get_current: User = Depends(get_current_user)):
    if get_current.role != "admin":
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "Acces refuse, uniquement accessible pour les admins")
    return get_current