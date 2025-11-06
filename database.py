from sqlmodel import create_engine, SQLModel, Session
import os # Ajout pour les variables d'environnement

# --- ATTENTION ---
# Pour le déploiement (Render), vous utiliserez des variables d'environnement.
# Pour le test local (Docker), cette URL est correcte.
# Ne jamais écrire un mot de passe de production en dur dans le code !
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/ma_db")

# Le "moteur" est l'objet central qui gère la connexion à la DB
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """
    Crée toutes les tables définies par SQLModel (celles avec table=True)
    si elles n'existent pas déjà.
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dépendance FastAPI pour "fournir" une session de base de données
    à chaque endpoint qui la demande.
    """
    with Session(engine) as session:
        yield session # "yield" fournit la session et attend la fin de l'endpoint