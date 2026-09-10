from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_admin
from app.models import Auteur, User
from typing import List
from app import schemas

router = APIRouter(prefix= "/auteurs", tags= ["auteurs"])

@router.get("/", response_model= List[schemas.AuteurResponse])
async def get_authors(db: AsyncSession = Depends(get_db)):
    authors = await db.execute(select(Auteur))
    authors = authors.scalars().all()
    if not authors:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Aucun auteur trouve")
    return authors

@router.post("/", status_code= status.HTTP_201_CREATED, response_model= schemas.AuteurResponse)
async def post_author(author: schemas.AuteurCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)):
    author_exist = await db.execute(select(Auteur).where(Auteur.nom == author.nom))
    author_exist = author_exist.scalar_one_or_none()
    if author_exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auteur déjà existante")
    new_author = Auteur(
        nom = author.nom,
        biographie = author.biographie,
        date_naissance = author.date_naissance
    )
    db.add(new_author)
    await db.commit()
    await db.refresh(new_author)
    return new_author
    
@router.delete("/{id}")
async def delete_author(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)):
    author = await db.execute(select(Auteur).where(id == Auteur.id))
    author = author.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Auteur introuvable")
    await db.delete(author)
    await db.commit()
    return {"message": "Auteur supprimer"}