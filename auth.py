from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
import os # Ajout pour la clé secrète

from database import get_session
from models import User

# --- Configuration de la Sécurité ---

# Contexte pour le hachage des mots de passe (nous utilisons bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schéma OAuth2 : indique à FastAPI comment trouver le token.
# "tokenUrl" est l'endpoint (relatif) où le client doit aller pour obtenir un token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Configuration des Tokens JWT ---

# NE JAMAIS écrire la clé secrète en dur.
# Utiliser une variable d'environnement.
SECRET_KEY = os.getenv("SECRET_KEY", "une_cle_secrete_tres_faible_pour_le_dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Le token expirera après 30 minutes

# --- Fonctions Utilitaires de Sécurité ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si un mot de passe en clair correspond au hachage."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hache un mot de passe."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Durée de vie par défaut si non fournie
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire}) # Ajoute la date d'expiration
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Fonctions de Dépendance ---

def get_user(session: Session, username: str) -> Optional[User]:
    """Récupère un utilisateur par son username depuis la DB."""
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session)
) -> User:
    """
    Dépendance principale pour la sécurité des endpoints.
    Décode le token, valide l'utilisateur et renvoie l'objet User.
    """
    # Exception standard en cas d'échec
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Décode le JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Le "sub" (sujet) de notre token est le username
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        # Si le token est malformé ou expiré
        raise credentials_exception
    
    # Trouve l'utilisateur dans la DB
    user = get_user(session, username=username)
    if user is None:
        # Si l'utilisateur n'existe plus (ex: compte supprimé)
        raise credentials_exception
    
    # Renvoie l'objet User, qui peut être utilisé dans l'endpoint
    return user

def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dépendance qui vérifie si l'utilisateur est
    connecté ET s'il est un administrateur.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="L'action demandée nécessite les droits administrateur"
        )
    return current_user