from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Reservation

async def activer_reservation(db: AsyncSession, livre_id: int):
    reservation = await db.execute(
        select(Reservation)
        .where(
            Reservation.livre_id == livre_id,
            Reservation.statut == "en_attente"
        )
        .order_by(Reservation.date_reservation)
    )
    reservation = reservation.scalar_one_or_none()
    if reservation:
        reservation.statut = "confirmee"
        await db.commit()