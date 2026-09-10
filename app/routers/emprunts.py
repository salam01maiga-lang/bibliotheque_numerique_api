from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.dependencies import get_db, get_current_user, require_admin
from app.models import Emprunt, User, Livre
from typing import List
from datetime import date
from app.services import emprunts_service
from app import schemas

router = APIRouter(prefix= "/emprunts", tags= ["emprunts"])

@router.post("/", status_code= status.HTTP_201_CREATED, response_model= schemas.EmpruntResponse)
async def emprunter(emprunt: schemas.EmpruntCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    livre = await db.execute(select(Livre).where(Livre.id == emprunt.livre_id))
    livre = livre.scalar_one_or_none()
    if not livre:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Livre introuvable")
    if livre.nb_disponible == 0:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Livre indisponible")
    livre.nb_disponible -= 1
    new_emprunt = Emprunt(
        user_id = current_user.id,
        livre_id = emprunt.livre_id,
        date_retour_prevue = emprunt.date_retour_prevue,
        statut = "en_cours"
    )
    db.add(new_emprunt)
    await db.commit()
    await db.refresh(new_emprunt)
    return new_emprunt

@router.put("/{id}/retour", response_model= schemas.EmpruntResponse)
async def edit_emprunt(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    emprunt_exist = await db.execute(select(Emprunt).where(id == Emprunt.id))
    emprunt_exist = emprunt_exist.scalar_one_or_none()
    if not emprunt_exist:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Emprunt introuvable")
    if emprunt_exist.user_id != current_user.id:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "Mauvais emprunt")
    if emprunt_exist.statut != "en_cours":
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Livre deja rendu")
    emprunt_exist.date_retour = date.today()
    emprunt_exist.statut = "rendu"
    livre = await db.execute(select(Livre).where(Livre.id == emprunt_exist.livre_id))
    livre = livre.scalar_one_or_none()
    livre.nb_disponible += 1
    await emprunts_service.activer_reservation(db, emprunt_exist.livre_id)
    await db.commit()
    await db.refresh(emprunt_exist)
    return emprunt_exist

@router.get("/mes-emprunts", response_model= List[schemas.EmpruntResponse])
async def get_my_emprunts(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    emprunts = await db.execute(select(Emprunt).where(Emprunt.user_id == current_user.id))
    emprunts = emprunts.scalars().all()
    return emprunts

@router.get("/", response_model= List[schemas.EmpruntResponse])
async def get_all_emprunts(db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)):
    emprunts = await db.execute(select(Emprunt))
    emprunts = emprunts.scalars().all()
    return emprunts
