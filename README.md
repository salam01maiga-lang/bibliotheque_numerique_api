# 📚 Digital Library API

A REST API for a digital library platform built with **FastAPI** and **PostgreSQL**, allowing users to browse books, borrow and return them, reserve unavailable titles, leave reviews, and manage favorites — all secured with JWT authentication.

## ✨ Features

- 🔐 **JWT Authentication** — registration, login (OAuth2 password flow), protected routes, role-based access (member / admin)
- 📖 **Book management** — full CRUD with category and multi-author linking, filterable listing (title, language, category, year, availability)
- ✍️ **Author management** — CRUD, linked to books through a many-to-many relationship
- 🗂️ **Category management** — create, list, delete
- 🔄 **Loans (emprunts)** — borrow a book, return it, automatic stock tracking, admin overview
- ⏳ **Reservations** — reserve a book when unavailable, automatically activated when a copy is returned
- ⭐ **Reviews (avis)** — leave and delete reviews per book
- ❤️ **Favorites** — save and remove favorite books
- 👤 **User profile** — view/update own profile, admin can list and activate/deactivate members

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| API Framework | FastAPI |
| Database | PostgreSQL (Neon) |
| ORM | SQLAlchemy (asynchronous) |
| Authentication | JWT (python-jose) + OAuth2 |
| Password hashing | Passlib (bcrypt) |
| Data validation | Pydantic v2 |
| ASGI server | Uvicorn |

## 📂 Project Structure

```
bibliotheque_numerique_api/
├── app/
│   ├── main.py                 # Application entry point
│   ├── database.py             # PostgreSQL async connection setup
│   ├── models.py                # SQLAlchemy models
│   ├── schemas.py               # Pydantic schemas (validation & serialization)
│   ├── core/
│   │   ├── config.py            # Configuration (environment variables)
│   │   ├── security.py          # Password hashing & JWT token handling
│   │   └── dependencies.py      # FastAPI dependencies (DB session, current user)
│   ├── services/
│   │   └── emprunts_service.py  # Reservation activation logic
│   └── routers/
│       ├── auth.py              # Registration, login
│       ├── users.py             # User profile, admin user management
│       ├── categories.py        # Category CRUD
│       ├── auteurs.py           # Author CRUD
│       ├── livres.py            # Book CRUD, filtering, author linking
│       ├── emprunts.py          # Loans and returns
│       ├── reservations.py      # Reservations
│       ├── avis.py              # Reviews
│       └── favoris.py           # Favorites
├── requirements.txt
└── .gitignore
```

## 🗃️ Data Model

The project has **9 related tables**:

- **User** — application users (members and admins)
- **Categorie** — book categories
- **Auteur** — book authors
- **Livre** — books in the library (linked to a category)
- **Livre_Auteur** — many-to-many link between books and authors
- **Emprunt** — loans (linked to a user and a book)
- **Reservation** — reservations for unavailable books
- **Avis** — reviews (linked to a user and a book)
- **Favoris** — favorites (linked to a user and a book)

## 🚀 Local Installation

### Prerequisites

- Python 3.12+
- A PostgreSQL database (local or a free instance like [Neon](https://neon.tech))

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/salam01maiga-lang/bibliotheque_numerique_api.git
cd bibliotheque_numerique_api
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file at the project root:
```
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**5. Run the server**
```bash
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`, with interactive Swagger docs at `http://localhost:8000/docs`.

## 📖 API Documentation

### 🔑 Authentication

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Log in and obtain a JWT token (OAuth2 form: username = email) | No |

### 👤 Users

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| GET | `/users/me` | Get the current user's profile | Yes |
| PUT | `/users/me` | Update the current user's profile | Yes |
| GET | `/users/` | List all members | Admin |
| PUT | `/users/{id}/activer` | Activate/deactivate a member | Admin |

### 🗂️ Categories

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| GET | `/categories/` | List all categories | No |
| POST | `/categories/` | Create a category | Admin |
| DELETE | `/categories/{id}` | Delete a category | Admin |

### ✍️ Authors

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| GET | `/auteurs/` | List all authors | No |
| POST | `/auteurs/` | Create an author | Admin |
| DELETE | `/auteurs/{id}` | Delete an author | Admin |

### 📖 Books

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| GET | `/livres/` | List books (filterable: title, language, category, year, availability) | No |
| GET | `/livres/{id}` | Get book details | No |
| POST | `/livres/` | Create a book (optionally with `auteurs_ids`) | Admin |
| PUT | `/livres/{id}` | Update a book | Admin |
| DELETE | `/livres/{id}` | Delete a book | Admin |

### 🔄 Loans

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/emprunts/` | Borrow a book | Yes |
| PUT | `/emprunts/{id}/retour` | Return a book | Yes |
| GET | `/emprunts/mes-emprunts` | List the current user's loans | Yes |
| GET | `/emprunts/` | List all loans | Admin |

### ⏳ Reservations

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/reservations/` | Reserve an unavailable book | Yes |
| DELETE | `/reservations/{id}` | Cancel a reservation | Yes |
| GET | `/reservations/mes-reservations` | List the current user's reservations | Yes |

### ⭐ Reviews

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/avis/` | Leave a review on a book | Yes |
| DELETE | `/avis/{id}` | Delete a review | Yes |
| GET | `/avis/livre/{livre_id}` | List reviews for a book | No |

### ❤️ Favorites

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/favoris/` | Add a book to favorites | Yes |
| DELETE | `/favoris/{id}` | Remove a favorite | Yes |
| GET | `/favoris/` | List the current user's favorites | Yes |

> 📘 Full interactive documentation (Swagger UI) with request examples is available at `/docs` once the server is running.

## 🔑 Usage Example

**1. Register**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nom": "Salam", "email": "salam@example.com", "mot_de_passe": "password123"}'
```

**2. Log in** (OAuth2 form — `username` field holds the email)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=salam@example.com&password=password123"
```

**3. Use the returned token to access protected routes**
```bash
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🌐 Deployment

- **Live API: https://bibliotheque-numerique-api.onrender.com
- **Live Swagger docs: https://bibliotheque-numerique-api.onrender.com/docs

> ⚠️ Hosted on Render's free tier — the service spins down after periods of inactivity, so the first request may take up to 60 seconds to respond while it wakes up. The database is hosted on [Neon](https://neon.tech), which scales to zero and wakes up automatically in under a second.

## 👤 Author

**Abdoul Salam Maiga** — Backend Developer — FastAPI / PostgreSQL

- GitHub: [@salam01maiga-lang](https://github.com/salam01maiga-lang)

## 📄 License

This project is open source and free to use for learning or demonstration purposes.
