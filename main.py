from fastapi import FastAPI
from database import create_db_and_tables
from routers import products, users, auth, variants, orders 

app = FastAPI(
    title="API E-Commerce de Madjiguene",
    description="L'API backend pour le projet de dropshipping.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# 3. Inclure les routeurs
app.include_router(products.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(variants.router)
app.include_router(orders.router) 

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API E-commerce ! Allez sur /docs pour la documentation."}