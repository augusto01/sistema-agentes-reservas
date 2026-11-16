import sqlite3

DB_NAME = "reservas.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de disponibilidad / servicios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            disponible INTEGER DEFAULT 1
        )
    """)
    
    # Tabla de reservas confirmadas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nombre TEXT NOT NULL,
            servicio_id INTEGER NOT NULL,
            estado TEXT DEFAULT 'CONFIRMADA',
            FOREIGN KEY (servicio_id) REFERENCES servicios(id)
        )
    """)
    
    # Datos semilla (seed) si está vacía
    cursor.execute("SELECT COUNT(*) FROM servicios")
    if cursor.fetchone()[0] == 0:
        datos_iniciales = [
            ("Cancha Básquet 1", "2026-11-20", "18:00", 1),
            ("Cancha Básquet 1", "2026-11-20", "19:00", 1),
            ("Sala de Reuniones A", "2026-11-20", "10:00", 1),
            ("Consultorio Médico 2", "2026-11-21", "09:30", 1),
        ]
        cursor.executemany(
            "INSERT INTO servicios (nombre, fecha, hora, disponible) VALUES (?, ?, ?, ?)",
            datos_iniciales
        )
    
    conn.commit()
    conn.close()