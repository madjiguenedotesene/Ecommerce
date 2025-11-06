from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    create_access_token, 
    get_user, 
    verify_password
)
from database import get_session

router = APIRouter(
    tags=["Authentification"] # Étiquette pour la documentation /docs
)

@router.post("/token")
def login_for_access_token(
    # FastAPI utilise OAuth2PasswordRequestForm pour récupérer
    # le username et password depuis un formulaire (form-data)
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session)
):
    """
    Endpoint de connexion (login).
    L'utilisateur envoie 'username' et 'password'.
    Le serveur renvoie un 'access_token' s'ils sont corrects.
    """
    # 1. Vérifie si l'utilisateur existe
    user = get_user(session, form_data.username)
    
    # 2. Vérifie si le mot de passe est correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Crée le token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 4. Renvoie le token
    return {"access_token": access_token, "token_type": "bearer"}