from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column
from sqlalchemy.types import JSON

# --- Modèles pour les Utilisateurs (Users) ---
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    is_admin: bool = Field(default=False) 

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    is_admin: bool


# --- Structure E-Commerce ---

# 1. Produit (Product)
class ProductBase(SQLModel):
    name: str
    description: Optional[str] = None
    image_urls: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))

class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    variants: List["Variant"] = Relationship(back_populates="product")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_urls: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))

class ProductRead(ProductBase):
    id: int

# 2. Variante (Variant)
class VariantBase(SQLModel):
    size: str = Field(index=True)
    color: str = Field(index=True)
    price: float
    alibaba_source_url: str = Field(index=True)
    stock_quantity: int = Field(default=0)
    product_id: int = Field(foreign_key="product.id")

class Variant(VariantBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product: Product = Relationship(back_populates="variants")

class VariantCreate(VariantBase):
    pass

# 3. Commande (Order)
class OrderItemBase(SQLModel):
    quantity: int = Field(gt=0)
    variant_id: int = Field(foreign_key="variant.id")
    order_id: int = Field(foreign_key="order.id")

class OrderItem(OrderItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    variant: "Variant" = Relationship()
    order: "Order" = Relationship(back_populates="items")

class OrderBase(SQLModel):
    status: str = Field(default="en_attente", index=True)
    user_id: int = Field(foreign_key="user.id")

class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: "User" = Relationship()
    items: List[OrderItem] = Relationship(back_populates="order")

class OrderUpdate(SQLModel):
    status: str

# 4. Modèles d'Entrée (Ce que le client envoie)
class OrderItemCreate(SQLModel):
    variant_id: int
    quantity: int

class OrderCreate(SQLModel):
    items: List[OrderItemCreate]


# ====================================================================
#  5. Modèles de Réponse (Ce que le serveur renvoie)
#  C'EST ICI QUE SE TROUVE LA CORRECTION
# ====================================================================

# --- 5A. Modèles PUBLICS (Cachent les infos secrètes) ---

class VariantRead(SQLModel):
    """
    Modèle PUBLIC pour une Variante.
    CACHE le lien Alibaba et le stock.
    """
    id: int
    size: str
    color: str
    price: float
    product_id: int
    # Note: 'alibaba_source_url' et 'stock_quantity' sont absents !

class ProductReadWithVariants(ProductBase):
    """
    Modèle PUBLIC pour un Produit (utilisé par GET /products/)
    """
    id: int
    variants: List[VariantRead] = [] # Utilise le modèle VariantRead PUBLIC

class OrderItemRead(OrderItemBase):
    id: int

class OrderItemReadWithVariant(OrderItemRead):
    """
    Modèle PUBLIC pour une ligne de commande
    """
    variant: VariantRead = None # Utilise le modèle VariantRead PUBLIC

class OrderRead(OrderBase):
    """
    Modèle PUBLIC pour une Commande (utilisé par POST /orders/ et GET /orders/me/)
    """
    id: int
    items: List[OrderItemReadWithVariant] = [] # Utilise le modèle PUBLIC

# --- 5B. Modèles ADMIN (Montrent tout) ---

class VariantReadAdmin(VariantBase):
    """
    Modèle ADMIN pour une Variante.
    Hérite de VariantBase (qui a TOUS les champs, y compris le lien)
    """
    id: int

class OrderItemReadAdmin(OrderItemRead):
    """
    Modèle ADMIN pour une ligne de commande
    """
    variant: VariantReadAdmin = None # Utilise le modèle VariantRead ADMIN

class OrderReadAdmin(OrderBase):
    """
    Modèle ADMIN pour une Commande (utilisé par GET /orders/ et PATCH /orders/id)
    """
    id: int
    items: List[OrderItemReadAdmin] = [] # Utilise le modèle ADMIN
    user: UserRead = None # L'admin peut voir qui a commandé