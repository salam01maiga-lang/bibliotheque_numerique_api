from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")

def hasher_mot_de_passe(mot_de_passe: str):
    return pwd_context.hash(mot_de_passe)

def verifier_hash(mot_de_passe: str, mot_de_passe_hasher: str):
    return pwd_context.verify(mot_de_passe, mot_de_passe_hasher)

def creer_access_token(data: dict):
    donnee = data.copy()
    expire = datetime.utcnow() + timedelta(minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    donnee.update({"exp": expire})
    return jwt.encode(donnee, settings.SECRET_KEY, algorithm= settings.ALGORITHM)

def verifier_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms= [settings.ALGORITHM])
        return payload
    except JWTError:
        return None