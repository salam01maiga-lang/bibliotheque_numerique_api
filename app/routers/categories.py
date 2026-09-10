from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, require_admin
from app.models import Categorie, User
from typing import List
from app import schemas

router = APIRouter(prefix= "/categories", tags= ["categories"])

@router.get("/", response_model= List[schemas.CategorieResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    categories = await db.execute(select(Categorie))
    categories = categories.scalars().all()
    if not categories:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Aucun categorie trouve")
    return categories

@router.post("/", status_code= status.HTTP_201_CREATED, response_model= schemas.CategorieResponse)
async def post_categorie(categorie: schemas.CategorieCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)):
    categorie_exist = await db.execute(select(Categorie).where(Categorie.nom == categorie.nom))
    categorie_exist = categorie_exist.scalar_one_or_none()
    if categorie_exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Catégorie déjà existante")
    new_categorie = Categorie(
        nom = categorie.nom,
        description = categorie.description
    )
    db.add(new_categorie)
    await db.commit()
    await db.refresh(new_categorie)
    return new_categorie
    
@router.delete("/{id}")
async def delete(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)):
    categorie = await db.execute(select(Categorie).where(id == Categorie.id))
    categorie = categorie.scalar_one_or_none()
    if not categorie:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "categorie introuvable")
    await db.delete(categorie)
    await db.commit()
    return {"message": "Categorie supprimer"}