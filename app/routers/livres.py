from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user, require_admin
from app.models import Livre, User, Livre_Auteur
from typing import List, Optional
from app import schemas

router = APIRouter(prefix= "/livres", tags= ["livres"])

@router.get("/", response_model= List[schemas.LivreResponse])
async def get_livres(
    db: AsyncSession = Depends(get_db),
    titre: Optional[str] = Query(None),
    langue: Optional[str] = Query(None),
    categorie_id: Optional[int] = Query(None),
    annee: Optional[int] = Query(None),
    disponible: Optional[bool] = Query(None),
):
    query = select(Livre).options(selectinload(Livre.categorie), selectinload(Livre.auteurs))
    if titre is not None:
        query = query.where(titre == Livre.titre)
    if langue is not None:
        query = query.where(langue == Livre.langue)
    if categorie_id is not None:
        query = query.where(categorie_id == Livre.categorie_id)
    if annee is not None:
        query = query.where(annee == Livre.annee)
    if disponible is not None:
        query = query.where(Livre.nb_disponible > 0)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{id}", response_model= schemas.LivreResponse)
async def get_livre(id: int , db: AsyncSession = Depends(get_db)):
    livre = await db.execute(select(Livre).where(id == Livre.id).options(selectinload(Livre.categorie), selectinload(Livre.auteurs)))
    livre = livre.scalar_one_or_none()
    if not livre:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "livre introuvable")
    return livre

@router.post("/", status_code= status.HTTP_201_CREATED, response_model= schemas.LivreResponse)
async def post_livre(livre: schemas.LivreCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)):
    new_livre = Livre(
    titre = livre.titre,
    description = livre.description,
    annee = livre.annee,
    isbn = livre.isbn,
    langue = livre.langue,
    nb_exemplaire = livre.nb_exemplaire,
    categorie_id = livre.categorie_id,
    imageCouverture = livre.imageCouverture,
    fichierPDF = livre.fichierPDF
    )
    db.add(new_livre)
    await db.commit()
    await db.refresh(new_livre, attribute_names=["categorie", "auteurs"])

    if livre.auteurs_ids:
        for auteur_id in livre.auteurs_ids:
            db.add(Livre_Auteur(livre_id=new_livre.id, auteur_id=auteur_id))
        await db.commit()
        await db.refresh(new_livre, attribute_names=["auteurs"])

    return new_livre

@router.put("/{id}", response_model= schemas.LivreResponse)
async def put_livre(id: int, livre: schemas.LivreUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)):
    livre_exist = await db.execute(select(Livre).where(id == Livre.id))
    livre_exist = livre_exist.scalar_one_or_none()
    if not livre_exist:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "livre introuvable")
    if livre.titre is not None:
        livre_exist.titre = livre.titre
    if livre.description is not None:
        livre_exist.description = livre.description
    if livre.annee is not None:
        livre_exist.annee = livre.annee
    if livre.isbn is not None:
        livre_exist.isbn = livre.isbn
    if livre.langue is not None:
        livre_exist.langue = livre.langue
    if livre.nb_exemplaire is not None:
        livre_exist.nb_exemplaire = livre.nb_exemplaire
    if livre.categorie_id is not None:
        livre_exist.categorie_id = livre.categorie_id
    if livre.imageCouverture is not None:
        livre_exist.imageCouverture = livre.imageCouverture
    if livre.fichierPDF is not None:
        livre_exist.fichierPDF = livre.fichierPDF
    await db.commit()
    await db.refresh(livre_exist, attribute_names=["categorie", "auteurs"])
    return livre_exist

@router.delete("/{id}")
async def delete_livre(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)):
    livre = await db.execute(select(Livre).where(id == Livre.id))
    livre = livre.scalar_one_or_none()
    if not livre:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "livre introuvable")
    await db.delete(livre)
    await db.commit()
    return {"message": f"Livre {id} supprimer avec succes"}