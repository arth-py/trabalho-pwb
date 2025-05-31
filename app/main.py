from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.db_utils import create_db_and_tables
from app.routes import auth, tasks

app = FastAPI(
    title="API de Tarefas Simples",
    description="Uma API para gerenciar tarefas com autenticação JWT.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tarefas"])

@app.on_event("startup")
def startup_event():
    create_db_and_tables()
