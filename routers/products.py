from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlmodel import Session, select

# Importer nos dépendances et modèles
from database import get_session
from models import (
    Product, 
    ProductCreate, 
    ProductRead, 
    ProductUpdate, 
    User,
    ProductReadWithVariants # <-- LE MODÈLE LE PLUS IMPORTANT
)
from auth import get_current_user

# 1. Créer le routeur
router = APIRouter(
    prefix="/products",
    tags=["Produits (Concept)"]
)

# --- Endpoint SÉCURISÉ (pour l'admin) ---
# Renvoie le produit AVEC sa liste (vide) de variantes
@router.post("/", response_model=ProductReadWithVariants, status_code=status.HTTP_201_CREATED) 
def create_product(
    product: ProductCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Crée un nouveau "Produit Concept" (ex: "Robe Courte").
    Il n'a ni prix, ni taille. Il sert de "conteneur" pour les variantes.
    """
    print(f"Produit créé par : {current_user.username}")
    
    db_product = Product.from_orm(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    
    return db_product

# --- Endpoint PUBLIC (Liste de tous les produits) ---
# MODIFIÉ pour renvoyer la liste des produits AVEC leurs variantes
@router.get("/", response_model=List[ProductReadWithVariants])
def read_products(session: Session = Depends(get_session)):
    """
    Lit tous les produits AVEC leurs variantes.
    C'est ce que votre page d'accueil affichera.
    """
    statement = select(Product)
    products = session.exec(statement).all()
    return products

# --- Endpoint PUBLIC (Un seul produit) ---
# MODIFIÉ pour renvoyer UN produit AVEC ses variantes
@router.get("/{product_id}", response_model=ProductReadWithVariants)
def read_product(product_id: int, session: Session = Depends(get_session)):
    """
    Lit un produit spécifique AVEC ses variantes.
    C'est ce que votre page de détail produit affichera.
    """
    # session.get() est intelligent et récupérera le produit
    # ET ses variantes associées grâce au "Relationship"
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return db_product

# --- Endpoints SÉCURISÉS (Update / Delete) ---
# (Ces endpoints peuvent renvoyer le ProductRead simple)

@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """ Met à jour les infos de base d'un produit (nom, description...). """
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value) 

    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@router.delete("/{product_id}", response_model=ProductRead)
def delete_product(
    product_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """ Supprime un produit. """
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    session.delete(db_product)
    session.commit()
    return db_product