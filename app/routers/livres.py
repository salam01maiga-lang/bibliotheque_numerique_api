from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user, require_admin
from sqlalchemy import delete
from app.models import Livre, User, Auteur, Livre_Auteur, Categorie, Emprunt, Reservation, Avis, Favoris
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
        if disponible:
            query = query.where(Livre.nb_disponible > 0)
        else:
            query = query.where(Livre.nb_disponible == 0)
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
    
    categorie = await db.execute(select(Categorie).where(Categorie.id == livre.categorie_id))
    categorie = categorie.scalar_one_or_none()
    if not categorie:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = "Categorie introuvable")
    
    isbn = await db.execute(select(Livre).where(Livre.isbn == livre.isbn))
    isbn = isbn.scalar_one_or_none()
    if isbn:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "ISBN existant")
    
    if livre.auteurs_ids:
        for auteur_id in livre.auteurs_ids:
            auteur = await db.execute(select(Auteur).where(Auteur.id == auteur_id))
            if not auteur.scalar_one_or_none():
                raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Auteur {auteur_id} introuvable")
    
    new_livre = Livre(
    titre = livre.titre,
    description = livre.description,
    annee = livre.annee,
    isbn = livre.isbn,
    langue = livre.langue,
    nb_exemplaire = livre.nb_exemplaire,
    nb_disponible = livre.nb_exemplaire,
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
        livre_existant = await db.execute(
            select(Livre).where(Livre.isbn == livre.isbn, Livre.id != id)
        )
        if livre_existant.scalar_one_or_none():
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "ISBN existant")
        livre_exist.isbn = livre.isbn
    if livre.langue is not None:
        livre_exist.langue = livre.langue
    if livre.nb_exemplaire is not None:
        difference = livre.nb_exemplaire - livre_exist.nb_exemplaire
        if livre_exist.nb_disponible + difference < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de descendre sous le nombre d'exemplaires empruntés"
            )
        livre_exist.nb_exemplaire = livre.nb_exemplaire
        livre_exist.nb_disponible += difference
    if livre.categorie_id is not None:
        categorie = await db.execute(select(Categorie).where(Categorie.id == livre.categorie_id))
        if not categorie.scalar_one_or_none():
            raison = "Categorie introuvable"
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= raison)
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
    for modele in (Emprunt, Reservation, Avis, Favoris):
        lie = await db.execute(select(modele).where(modele.livre_id == id))
        if lie.scalars().first():
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST,
                detail= "Impossible de supprimer : ce livre a des emprunts, reservations, avis ou favoris"
            )
    await db.execute(delete(Livre_Auteur).where(Livre_Auteur.livre_id == id))
    await db.delete(livre)
    await db.commit()
    return {"message": f"Livre {id} supprimer avec succes"}