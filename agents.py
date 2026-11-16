import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import consultar_disponibilidad, crear_reserva, cancelar_reserva

# Carga el .env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

MODEL_ID = "gemini-2.0-flash"

def _get_client() -> genai.Client:
    """Inicializa el cliente de Gemini aceptando cualquier formato de token (AQ o AIza)."""
    load_dotenv(dotenv_path=env_path, override=True)
    api_key = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
    if not api_key:
        raise RuntimeError(f"Falta configurar GEMINI_API_KEY en {env_path}")
    
    # Forzamos la creación del cliente con la clave del .env sin validar prefijos estrictos
    return genai.Client(api_key=api_key)

def agente_supervisor(mensaje_usuario: str) -> str:
    """Clasifica la intención y delega al agente especialista correspondiente."""
    client = _get_client()
    prompt_router = f"""
    Clasifica la siguiente solicitud del usuario en UNA de estas categorías exactas:
    - CONSULTA (si pregunta horarios, fechas o disponibilidad)
    - RESERVA (si quiere agendar, reservar o cancelar un turno)
    - GENERAL (saludos o preguntas fuera de dominio)
    
    Responde ÚNICAMENTE con la palabra de la categoría.
    Mensaje: "{mensaje_usuario}"
    """
    resp = client.models.generate_content(model=MODEL_ID, contents=prompt_router)
    intencion = resp.text.strip().upper()
    
    if "CONSULTA" in intencion:
        return agente_disponibilidad(mensaje_usuario)
    elif "RESERVA" in intencion:
        return agente_gestion_reservas(mensaje_usuario)
    else:
        return agente_recepcion(mensaje_usuario)

def agente_disponibilidad(mensaje: str) -> str:
    """Agente especialista en consultar horarios y disponibilidad."""
    client = _get_client()
    config = types.GenerateContentConfig(
        system_instruction="Eres el Agente de Disponibilidad. Usa tus herramientas para consultar turnos libres y responde de forma clara y amable.",
        tools=[consultar_disponibilidad],
        temperature=0.2,
    )
    resp = client.models.generate_content(model=MODEL_ID, contents=mensaje, config=config)
    return resp.text

def agente_gestion_reservas(mensaje: str) -> str:
    """Agente especialista en altas y bajas de reservas."""
    client = _get_client()
    config = types.GenerateContentConfig(
        system_instruction=(
            "Eres el Agente de Gestión de Reservas. Puedes crear o cancelar reservas usando tus herramientas. "
            "Si el usuario no dio su nombre o el ID del turno, pídelo antes de ejecutar la reserva."
        ),
        tools=[consultar_disponibilidad, crear_reserva, cancelar_reserva],
        temperature=0.1,
    )
    resp = client.models.generate_content(model=MODEL_ID, contents=mensaje, config=config)
    return resp.text

def agente_recepcion(mensaje: str) -> str:
    """Agente de bienvenida y soporte general."""
    client = _get_client()
    config = types.GenerateContentConfig(
        system_instruction="Eres el Recepcionista Virtual del sistema de reservas. Explica brevemente que puedes consultar disponibilidad, crear reservas y cancelarlas.",
        temperature=0.5,
    )
    resp = client.models.generate_content(model=MODEL_ID, contents=mensaje, config=config)
    return resp.text