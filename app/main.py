from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import users, auth, avis, emprunts,auteurs, favoris, livres, reservations, categories
from app.database import engine, Base
import app.models as models

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500"],
    allow_credentials= True,
    allow_methods= ["*"],
    allow_headers= ["*"],
)

app.include_router(auth.router)
app.include_router(avis.router)
app.include_router(users.router)
app.include_router(emprunts.router)
app.include_router(favoris.router)
app.include_router(reservations.router)
app.include_router(livres.router)
app.include_router(categories.router)
app.include_router(auteurs.router)

