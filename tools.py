import sqlite3
from database import DB_NAME

def consultar_disponibilidad(fecha: str = "") -> str:
    """Consulta los turnos o servicios disponibles. Opcionalmente filtra por fecha (YYYY-MM-DD)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if fecha:
        cursor.execute(
            "SELECT id, nombre, fecha, hora FROM servicios WHERE disponible = 1 AND fecha = ?",
            (fecha,)
        )
    else:
        cursor.execute("SELECT id, nombre, fecha, hora FROM servicios WHERE disponible = 1")
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No hay disponibilidad para los criterios consultados."
    
    resultado = "Turnos disponibles:\n"
    for r in rows:
        resultado += f"- ID: {r[0]} | {r[1]} | Fecha: {r[2]} | Hora: {r[3]}\n"
    return resultado

def crear_reserva(cliente_nombre: str, servicio_id: int) -> str:
    """Crea una reserva para un cliente dado el ID de un servicio disponible."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT nombre, fecha, hora, disponible FROM servicios WHERE id = ?", (servicio_id,))
    servicio = cursor.fetchone()
    
    if not servicio:
        conn.close()
        return f"Error: No existe el servicio con ID {servicio_id}."
    if servicio[3] == 0:
        conn.close()
        return f"Error: El servicio '{servicio[0]}' ya no está disponible."
    
    cursor.execute(
        "INSERT INTO reservas (cliente_nombre, servicio_id) VALUES (?, ?)",
        (cliente_nombre, servicio_id)
    )
    reserva_id = cursor.lastrowid
    cursor.execute("UPDATE servicios SET disponible = 0 WHERE id = ?", (servicio_id,))
    
    conn.commit()
    conn.close()
    return f"Reserva #{reserva_id} CONFIRMADA para {cliente_nombre}: {servicio[0]} el {servicio[1]} a las {servicio[2]}."

def cancelar_reserva(reserva_id: int) -> str:
    """Cancela una reserva existente por su ID y libera el turno."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT servicio_id, estado FROM reservas WHERE id = ?", (reserva_id,))
    reserva = cursor.fetchone()
    
    if not reserva:
        conn.close()
        return f"No se encontró la reserva #{reserva_id}."
    if reserva[1] == "CANCELADA":
        conn.close()
        return f"La reserva #{reserva_id} ya estaba cancelada."
    
    cursor.execute("UPDATE reservas SET estado = 'CANCELADA' WHERE id = ?", (reserva_id,))
    cursor.execute("UPDATE servicios SET disponible = 1 WHERE id = ?", (reserva[0],))
    
    conn.commit()
    conn.close()
    return f"Reserva #{reserva_id} CANCELADA exitosamente. El turno vuelve a estar disponible."