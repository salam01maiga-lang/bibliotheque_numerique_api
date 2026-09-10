from sqlalchemy import ForeignKey, Column, Boolean, DateTime, Integer, Float, String, Text, Date
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key= True)
    nom = Column(String(32), nullable= False, index= True)
    email = Column(String(100), nullable= False, unique= True, index= True)
    mot_de_passe = Column(String(70), nullable= False)
    role = Column(String(100), nullable= False)
    date_creation = Column(DateTime, default= datetime.utcnow)
    est_actif = Column(Boolean, default= True)

    emprunts = relationship("Emprunt", back_populates= "user")
    avis = relationship("Avis", back_populates= "user")
    reservations = relationship("Reservation", back_populates= "user")
    favoris = relationship("Favoris", back_populates="user")

class Emprunt(Base):
    __tablename__ = "emprunts"

    id = Column(Integer, primary_key= True)
    date_emprunt = Column(DateTime, default= datetime.utcnow)
    date_retour_prevue = Column(DateTime)
    date_retour = Column(DateTime)
    statut = Column(String(100))
    user_id = Column(Integer, ForeignKey("users.id"))
    livre_id = Column(Integer, ForeignKey("livres.id"))

    user = relationship("User", back_populates="emprunts")
    livre = relationship("Livre", back_populates="emprunts")

class Avis(Base):
    __tablename__ = "avis"

    id = Column(Integer, primary_key= True)
    note = Column(Integer, nullable= False)
    commentaire = Column(Text)
    date_creation = Column(DateTime, default= datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    livre_id = Column(Integer, ForeignKey("livres.id"))

    user = relationship("User", back_populates="avis")
    livre = relationship("Livre", back_populates="avis")

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key= True)
    date_reservation = Column(DateTime, default= datetime.utcnow)
    statut = Column(String(50), default= "en_attente")
    user_id = Column(Integer, ForeignKey("users.id"))
    livre_id = Column(Integer, ForeignKey("livres.id"))

    user = relationship("User", back_populates="reservations")
    livre = relationship("Livre", back_populates="reservations")

class Favoris(Base):
    __tablename__ = "favoris"

    id = Column(Integer, primary_key=True)
    date_ajout = Column(DateTime, default= datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    livre_id = Column(Integer, ForeignKey("livres.id"))

    user = relationship("User", back_populates="favoris")
    livre = relationship("Livre", back_populates="favoris")

class Livre(Base):
    __tablename__ = "livres"

    id = Column(Integer, primary_key= True)
    titre = Column(String(250), nullable= False, index= True)
    description = Column(Text)
    annee = Column(Integer, nullable= False, index= True)
    isbn = Column(String(20), unique=True, nullable=False)
    langue = Column(String(100), nullable= False)
    imageCouverture = Column(String(500), nullable= False)
    fichierPDF = Column(String(500), nullable= False)
    nb_exemplaire = Column(Integer, nullable=False, default= 1)
    nb_disponible = Column(Integer, nullable=False, default= 1)
    date_ajout = Column(DateTime, default= datetime.utcnow)
    categorie_id = Column(Integer, ForeignKey("categories.id"))

    categorie = relationship("Categorie", back_populates="livres")
    livre_auteur = relationship("Livre_Auteur", back_populates="livre")
    auteurs = relationship(
        "Auteur",
        secondary="livre_auteur",
        back_populates="livres",
        viewonly=True
    )
    emprunts = relationship("Emprunt", back_populates= "livre")
    avis = relationship("Avis", back_populates="livre")
    reservations = relationship("Reservation", back_populates= "livre")
    favoris = relationship("Favoris", back_populates="livre")

class Livre_Auteur(Base):
    __tablename__ = "livre_auteur"

    id = Column(Integer, primary_key= True)
    livre_id = Column(Integer, ForeignKey("livres.id"))
    auteur_id = Column(Integer, ForeignKey("auteurs.id"))

    livre = relationship("Livre", back_populates="livre_auteur")
    auteur = relationship("Auteur", back_populates= "livre_auteur")

class Auteur(Base):
    __tablename__ = "auteurs"

    id = Column(Integer, primary_key= True)
    nom = Column(String(100), nullable= False, index= True)
    biographie = Column(Text)
    date_naissance = Column(Date)

    livre_auteur = relationship("Livre_Auteur", back_populates="auteur")
    livres = relationship(
        "Livre",
        secondary="livre_auteur",
        back_populates="auteurs",
        viewonly=True
    )

class Categorie(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key= True)
    nom = Column(String(300), nullable= False, index= True)
    description = Column(Text)

    livres = relationship("Livre", back_populates= "categorie")