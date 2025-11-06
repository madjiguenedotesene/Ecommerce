from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlmodel import Session, select

# Importer nos dépendances et modèles
from database import get_session
from models import (
    User,
    Variant,
    VariantCreate,
    VariantRead,
    Product # On a besoin de Product pour vérifier que le produit existe
)
from auth import get_current_user

# 1. Créer le routeur
router = APIRouter(
    prefix="/variants",
    tags=["Variantes (Taille, Couleur, Prix)"] # Étiquette pour les /docs
)

# --- Endpoint SÉCURISÉ (pour l'admin) ---
@router.post("/", response_model=VariantRead, status_code=status.HTTP_201_CREATED)
def create_variant(
    variant: VariantCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Ajoute une nouvelle variante (ex: Taille S, Couleur Kaki, 25.99€)
    à un produit existant.
    
    Vous devez fournir le 'product_id' du produit parent.
    """
    
    # Étape 1: Vérifier que le produit parent (ex: ID 1) existe
    product = session.get(Product, variant.product_id)
    if not product:
        raise HTTPException(
            status_code=404, 
            detail=f"Produit avec ID {variant.product_id} non trouvé."
        )
    
    # Étape 2: Créer la variante
    # Note: 'variant' est un 'VariantCreate' qui contient
    # size, color, price, alibaba_source_url, stock_quantity, et product_id
    db_variant = Variant.from_orm(variant)
    
    session.add(db_variant)
    session.commit()
    session.refresh(db_variant)
    
    print(f"Variante créée par: {current_user.username}")
    return db_variant

# --- Endpoint PUBLIC (pour voir une variante spécifique) ---
@router.get("/{variant_id}", response_model=VariantRead)
def read_variant(variant_id: int, session: Session = Depends(get_session)):
    """
    Lit les détails d'une variante spécifique par son ID.
    """
    db_variant = session.get(Variant, variant_id)
    if not db_variant:
        raise HTTPException(status_code=404, detail="Variante non trouvée")
    return db_variant