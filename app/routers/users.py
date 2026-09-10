from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.dependencies import get_db, get_current_user, require_admin
from app.models import User
from typing import List
from app import schemas

router = APIRouter(prefix= "/users", tags= ["users"])

@router.get("/me", response_model= schemas.UserResponse)
async def profil(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model= schemas.UserResponse)
async def profil_edit(user: schemas.UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user.nom is not None:
        current_user.nom = user.nom
    if user.email is not None:
        current_user.email = user.email
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.get("/", response_model= List[schemas.UserResponse])
async def display_users(db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
   result = await db.execute(select(User).where(User.role != "admin"))
   return result.scalars().all()

@router.put("/{id}/activer")
async def activer_desactiver_membre(id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    membre = await db.execute(select(User).where(User.id == id))
    membre = membre.scalar_one_or_none()
    if not membre:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Utilisateur introuvable")
    membre.est_actif = not membre.est_actif
    await db.commit()
    await db.refresh(membre)
    return membre
