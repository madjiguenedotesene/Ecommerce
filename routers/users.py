from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select # <-- AJOUTEZ "select"
from models import User, UserCreate, UserRead
from database import get_session
from auth import get_password_hash, get_user

router = APIRouter(
    prefix="/users",
    tags=["Utilisateurs"]
)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """
    Crée un nouvel utilisateur (inscription).
    Le TOUT PREMIER utilisateur (ID 1) sera admin.
    """
    # ... (la vérification 'if db_user:' ne change pas)
    db_user = get_user(session, user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris"
        )
    
    hashed_password = get_password_hash(user.password)
    
    # --- ↓↓↓ LOGIQUE ADMIN AJOUTÉE ↓↓↓ ---
    # On vérifie si c'est le tout premier utilisateur
    statement = select(User)
    first_user = session.exec(statement).first()
    is_first_user = first_user is None
    # --- ↑↑↑ FIN LOGIQUE ADMIN ↑↑↑ ---

    # Crée l'objet User pour la DB
    db_user = User(
        username=user.username, 
        hashed_password=hashed_password,
        # Le premier utilisateur est admin par défaut
        is_admin=is_first_user 
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user