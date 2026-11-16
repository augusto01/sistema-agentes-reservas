from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from database import init_db
from agents import agente_supervisor

load_dotenv()
init_db()

app = FastAPI(
    title="Sistema Multi-Agente de Reservas",
    description="API de orquestación de agentes inteligentes con Tool Calling y SQLite.",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    mensaje: str

class ChatResponse(BaseModel):
    respuesta: str

@app.post("/chat", response_model=ChatResponse)
def conversar_con_agentes(req: ChatRequest):
    respuesta = agente_supervisor(req.mensaje)
    return ChatResponse(respuesta=respuesta)