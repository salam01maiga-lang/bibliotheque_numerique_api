from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

#============ USERS =============

class UserBase(BaseModel):
    nom: str
    email: str

class UserCreate(UserBase):
    mot_de_passe: str

class UserResponse(UserBase):
    id: int
    role: str
    est_actif: bool
    date_creation: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    nom: Optional[str] = None
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    mot_de_passe: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int
    role: str

#============ CATEGORIE =============

class CategorieBase(BaseModel):
    nom: str
    description: str

class CategorieCreate(CategorieBase):
    pass

class CategorieResponse(CategorieBase):
    id: int

    class Config:
        from_attributes = True

#============= AUTEURS ============

class AuteurBase(BaseModel):
    nom: str
    biographie: str
    date_naissance: date

class AuteurCreate(AuteurBase):
    pass 

class AuteurResponse(AuteurBase):
    id: int

    class Config:
        from_attributes = True


#============ LIVRES ============

class LivreBase(BaseModel):
    titre: str
    description: str
    annee: int
    isbn: str
    langue: str
    nb_exemplaire: int
    categorie_id: int

class LivreCreate(LivreBase):
    imageCouverture: str
    fichierPDF: str
    auteurs_ids: Optional[List[int]] = None

class LivreResponse(LivreBase):
    id: int 
    nb_disponible: int
    date_ajout: datetime
    categorie: CategorieResponse
    auteurs: List[AuteurResponse]

    class Config:
        from_attributes = True

class LivreUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    annee: Optional[int] = None
    isbn: Optional[str] = None
    langue: Optional[str] = None
    nb_exemplaire: Optional[int] = None
    categorie_id: Optional[int] = None
    imageCouverture: Optional[str] = None
    fichierPDF: Optional[str] = None

#=========== EMPRUNT =============

class EmpruntBase(BaseModel):
    livre_id: int
    date_retour_prevue: date

class EmpruntCreate(EmpruntBase):
    pass

class EmpruntResponse(EmpruntBase):
    id: int
    user_id: int
    date_emprunt: datetime
    date_retour: Optional[datetime] = None
    statut: str

    class Config:
        from_attributes = True

#============ RESERVATION =========
class ReservationCreate(BaseModel):
    livre_id: int

class ReservationResponse(BaseModel):
    id: int
    user_id: int
    livre_id: int
    date_reservation: date
    statut: str

    class Config:
        from_attributes = True

#=========== AVIS =================

class AvisBase(BaseModel):
    livre_id: int
    note: int
    commentaire: str

class AvisCreate(AvisBase):
    pass 

class AvisResponse(AvisBase):
    id: int
    user_id: int
    date_creation: date

    class Config:
        from_attributes = True

#========== FAVORIS ==============

class FavorisCreate(BaseModel):
    livre_id: int

class FavorisResponse(BaseModel):
    id: int
    user_id: int
    livre_id: int
    date_ajout: date

    class Config:
        from_attributes = True