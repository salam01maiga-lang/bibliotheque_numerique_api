from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.models import Favoris, User, Livre
from typing import List
from app import schemas

router = APIRouter(prefix= "/favoris", tags= ["favoris"])

@router.post("/", response_model= schemas.FavorisResponse)
async def post_favoris(favoris: schemas.FavorisCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    favoris_exist = await db.execute(select(Favoris).where(
        favoris.livre_id == Favoris.livre_id,
        Favoris.user_id == current_user.id))
    favoris_exist = favoris_exist.scalar_one_or_none()
    if favoris_exist:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "deja en favoris")
    new_favoris = Favoris(
        user_id = current_user.id,
        livre_id = favoris.livre_id
    )
    db.add(new_favoris)
    await db.commit()
    await db.refresh(new_favoris)
    return new_favoris

@router.delete("/{id}")
async def delete_favoris(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    favoris = await db.execute(select(Favoris).where(
        id == Favoris.id,
        Favoris.user_id == current_user.id))
    favoris = favoris.scalar_one_or_none()
    if not favoris:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "favoris introuvable")
    await db.delete(favoris)
    await db.commit()
    return {"message": "favoris supprimer"}

@router.get("/", response_model= List[schemas.FavorisResponse])
async def get_avis_livre (db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    favoris = await db.execute(select(Favoris).where(Favoris.user_id == current_user.id))
    favoris = favoris.scalars().all()
    if not favoris:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Aucun favoris trouve")
    return favoris