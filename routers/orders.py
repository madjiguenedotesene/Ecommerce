from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlmodel import Session, select

from database import get_session
from models import (
    User, Order, OrderCreate, OrderUpdate, Variant, OrderItem,
    OrderRead, # Le modèle PUBLIC
    OrderReadAdmin # <-- Le NOUVEAU modèle ADMIN
)
from auth import get_current_user, get_current_admin_user 

router = APIRouter(
    prefix="/orders",
    tags=["Commandes (Panier)"]
)

# --- Endpoint CLIENT ---
@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Crée une nouvelle commande.
    Renvoie le modèle PUBLIC (OrderRead)
    """
    
    db_order = Order(user_id=current_user.id, status="en_attente")
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    
    for item_data in order_data.items:
        variant = session.get(Variant, item_data.variant_id)
        if not variant:
            raise HTTPException(
                status_code=404, 
                detail=f"Variante avec ID {item_data.variant_id} non trouvée."
            )
        if variant.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuffisant pour {variant.size} {variant.color}."
            )
        
        db_item = OrderItem(
            quantity=item_data.quantity,
            variant_id=item_data.variant_id,
            order_id=db_order.id
        )
        
        variant.stock_quantity -= item_data.quantity
        session.add(variant)
        session.add(db_item)
        
    session.commit()
    session.refresh(db_order)
    return db_order

# --- Endpoint CLIENT ---
@router.get("/me/", response_model=List[OrderRead])
def read_my_orders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les commandes du client.
    Renvoie le modèle PUBLIC (OrderRead)
    """
    statement = select(Order).where(Order.user_id == current_user.id)
    orders = session.exec(statement).all()
    return orders

# --- Endpoint ADMIN ---
# ↓↓↓ MODIFIÉ ICI ↓↓↓
@router.get("/", response_model=List[OrderReadAdmin]) 
def read_all_orders(
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    [ADMIN SEULEMENT]
    Récupère TOUTES les commandes.
    Renvoie le modèle ADMIN (avec tous les détails)
    """
    print(f"Action Admin par: {admin_user.username}")
    statement = select(Order)
    orders = session.exec(statement).all()
    return orders

# --- Endpoint ADMIN ---
# ↓↓↓ MODIFIÉ ICI ↓↓↓
@router.patch("/{order_id}", response_model=OrderReadAdmin)
def update_order_status(
    order_id: int,
    order_update: OrderUpdate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    [ADMIN SEULEMENT]
    Met à jour le statut d'une commande.
    Renvoie le modèle ADMIN (avec tous les détails)
    """
    db_order = session.get(Order, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    db_order.status = order_update.status
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    
    print(f"Commande {order_id} mise à jour par: {admin_user.username}")
    return db_order