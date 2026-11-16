import os
from google import genai
from google.genai import types
from tools import consultar_disponibilidad, crear_reserva, cancelar_reserva

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "gemini-2.5-flash"

def agente_supervisor(mensaje_usuario: str) -> str:
    """Clasifica la intención y delega al agente especialista correspondiente."""
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
    config = types.GenerateContentConfig(
        system_instruction="Eres el Agente de Disponibilidad. Usa tus herramientas para consultar turnos libres y responde de forma clara y amable.",
        tools=[consultar_disponibilidad],
        temperature=0.2,
    )
    resp = client.models.generate_content(model=MODEL_ID, contents=mensaje, config=config)
    return resp.text

def agente_gestion_reservas(mensaje: str) -> str:
    """Agente especialista en altas y bajas de reservas."""
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
    config = types.GenerateContentConfig(
        system_instruction="Eres el Recepcionista Virtual del sistema de reservas. Explica brevemente que puedes consultar disponibilidad, crear reservas y cancelarlas.",
        temperature=0.5,
    )
    resp = client.models.generate_content(model=MODEL_ID, contents=mensaje, config=config)
    return resp.text