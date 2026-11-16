from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import sqlite3
from database import init_db, DB_NAME
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

@app.get("/", response_class=HTMLResponse)
def home():
    """Sirve la interfaz gráfica moderna del sistema."""
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/turnos")
def listar_turnos_bd():
    """Devuelve los registros actuales de SQLite para el panel en vivo."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, fecha, hora, disponible FROM servicios")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "nombre": r[1], "fecha": r[2], "hora": r[3], "disponible": bool(r[4])}
        for r in rows
    ]

@app.post("/chat", response_model=ChatResponse)
def conversar_con_agentes(req: ChatRequest):
    try:
        respuesta = agente_supervisor(req.mensaje)
        return ChatResponse(respuesta=respuesta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))