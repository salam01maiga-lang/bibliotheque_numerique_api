from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.dependencies import get_db, get_current_user
from app.models import User, Reservation, Livre
from typing import List
from app import schemas

router = APIRouter(prefix= "/reservations", tags= ["reservations"])

@router.post("/", response_model= schemas.ReservationResponse)
async def reserver(reservation: schemas.ReservationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    livre = await db.execute(select(Livre).where(Livre.id == reservation.livre_id,))
    livre = livre.scalar_one_or_none()
    if not livre:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Livre introuvable")
    if livre.nb_disponible > 0:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Emprunt possible")
    reservation_exist = await db.execute(select(Reservation).where(
        Reservation.user_id == current_user.id,
        Reservation.livre_id == reservation.livre_id))
    reservation_exist = reservation_exist.scalar_one_or_none()
    if reservation_exist:
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "Vous avez deja reserver ce livre")
    new_reservation = Reservation(
        user_id = current_user.id,
        livre_id = reservation.livre_id
    )
    db.add(new_reservation)
    await db.commit()
    await db.refresh(new_reservation)
    return new_reservation

@router.delete("/{id}")
async def delete_reservation(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    reservation_exist = await db.execute(select(Reservation).where(
        id == Reservation.id,
        Reservation.user_id == current_user.id))
    reservation_exist = reservation_exist.scalar_one_or_none()
    if not reservation_exist:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Reservation introuvable")
    await db.delete(reservation_exist)
    await db.commit()
    return {"message": "Reservation supprimer"}

@router.get("/mes-reservations", response_model= List[schemas.ReservationResponse])
async def get_reservations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    reservations = await db.execute(select(Reservation).where(Reservation.user_id == current_user.id))
    reservations = reservations.scalars().all()
    return reservations

