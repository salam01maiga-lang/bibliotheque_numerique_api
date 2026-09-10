from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.models import Avis, User, Livre
from typing import List
from app import schemas

router = APIRouter(prefix= "/avis", tags= ["avis"])

@router.post("/", response_model= schemas.AvisResponse)
async def faire_avis(avis: schemas.AvisCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    livre = await db.execute(select(Livre).where(Livre.id == avis.livre_id))
    livre = livre.scalar_one_or_none()
    if not livre:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Livre introuvable")
    new_avis = Avis(
        user_id = current_user.id,
        livre_id = avis.livre_id,
        note = avis.note,
        commentaire = avis.commentaire
    )
    db.add(new_avis)
    await db.commit()
    await db.refresh(new_avis)
    return new_avis

@router.delete("/{id}")
async def delete_avis(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    avis = await db.execute(select(Avis).where(
        id == Avis.id,
        Avis.user_id == current_user.id))
    avis = avis.scalar_one_or_none()
    if not avis:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "avis introuvable")
    await db.delete(avis)
    await db.commit()
    return {"message": "avis supprimer"}

@router.get("/livre/{livre_id}", response_model= List[schemas.AvisResponse])
async def get_avis_livre(livre_id: int, db: AsyncSession = Depends(get_db)):
    avis = await db.execute(select(Avis).where(Avis.livre_id == livre_id))
    avis = avis.scalars().all()
    if not avis:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Aucun avis trouve")
    return avis