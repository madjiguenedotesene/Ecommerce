# API Backend pour E-Commerce (FastAPI)

Ceci est le code backend pour un projet de site e-commerce moderne, basé sur un modèle de dropshipping.

L'API est construite avec **FastAPI** et **PostgreSQL** (via SQLModel) et gère l'intégralité de la logique métier :

* **Gestion des Produits :** Structure Produit (concept) -> Variantes (taille, couleur, prix, stock).
* **Dropshipping :** Les variantes incluent un champ  secret, visible uniquement par l'administrateur.
* **Authentification :** Gestion des rôles (JWT) pour distinguer les Clients (peuvent commander) des Admins (peuvent gérer les produits et voir les commandes).
* **Gestion des Commandes :** Création de commandes avec déduction automatique du stock.

Ce projet est conçu pour être déployé sur **Render** (via Docker/Gunicorn) et être consommé par un frontend (React/Next.js).

**Statut :** API déployée sur Render.
# API Backend pour E-Commerce (FastAPI)

Ceci est le code backend pour un projet de site e-commerce moderne, basé sur un modèle de dropshipping.

L'API est construite avec **FastAPI** et **PostgreSQL** (via SQLModel) et gère l'intégralité de la logique métier :

* **Gestion des Produits :** Structure Produit (concept) -> Variantes (taille, couleur, prix, stock).
* **Dropshipping :** Les variantes incluent un champ  secret, visible uniquement par l'administrateur.
* **Authentification :** Gestion des rôles (JWT) pour distinguer les Clients (peuvent commander) des Admins (peuvent gérer les produits et voir les commandes).
* **Gestion des Commandes :** Création de commandes avec déduction automatique du stock.

Ce projet est conçu pour être déployé sur **Render** (via Docker/Gunicorn) et être consommé par un frontend (React/Next.js).

**Statut :** API déployée sur Render.
