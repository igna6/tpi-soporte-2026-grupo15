import sqlite3
import os
from datetime import datetime

# Archivo de base de datos local
DB_PATH = 'inversiones.db'

def get_connection():
    """Devuelve una conexión a la base de datos SQLite."""
    return sqlite3.connect(DB_PATH)

def inicializar_db():
    """Crea las tablas necesarias si no existen."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla Inversor
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Inversor (
            id_inversor INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT NOT NULL,
            saldo_efectivo REAL NOT NULL,
            fecha_creacion TEXT NOT NULL
        )
    ''')

    # Tabla ActivoFinanciero
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ActivoFinanciero (
            ticker TEXT PRIMARY KEY,
            nombre_empresa TEXT NOT NULL,
            tipo_activo TEXT NOT NULL
        )
    ''')

    # Tabla Transaccion (Historial inmutable)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transaccion (
            id_transaccion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_inversor INTEGER NOT NULL,
            ticker_activo TEXT NOT NULL,
            tipo_operacion TEXT NOT NULL,
            cantidad REAL NOT NULL,
            precio_unitario_ejecucion REAL NOT NULL,
            fecha_hora TEXT NOT NULL,
            FOREIGN KEY (id_inversor) REFERENCES Inversor(id_inversor),
            FOREIGN KEY (ticker_activo) REFERENCES ActivoFinanciero(ticker)
        )
    ''')

    # Tabla Posicion (Tenencia actual consolidada)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Posicion (
            id_posicion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_inversor INTEGER NOT NULL,
            ticker_activo TEXT NOT NULL,
            cant_actual REAL NOT NULL,
            prec_prom_compra REAL NOT NULL,
            FOREIGN KEY (id_inversor) REFERENCES Inversor(id_inversor),
            FOREIGN KEY (ticker_activo) REFERENCES ActivoFinanciero(ticker)
        )
    ''')
    
    # Crear un inversor por defecto si la tabla está vacía
    cursor.execute('SELECT COUNT(*) FROM Inversor')
    if cursor.fetchone()[0] == 0:
        fecha_actual = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO Inversor (nombre_usuario, saldo_efectivo, fecha_creacion)
            VALUES (?, ?, ?)
        ''', ('Usuario_Demo', 10000.0, fecha_actual))

    conn.commit()
    conn.close()

# --- MÉTODOS CRUD (Acceso directo a datos sin ORM) ---

def obtener_inversor(id_inversor: int) -> dict:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Inversor WHERE id_inversor = ?', (id_inversor,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def actualizar_saldo_inversor(id_inversor: int, nuevo_saldo: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Inversor SET saldo_efectivo = ? WHERE id_inversor = ?', (nuevo_saldo, id_inversor))
    conn.commit()
    conn.close()

def obtener_posiciones(id_inversor: int) -> list:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Posicion WHERE id_inversor = ?', (id_inversor,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def obtener_posicion(id_inversor: int, ticker: str) -> dict:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Posicion WHERE id_inversor = ? AND ticker_activo = ?', (id_inversor, ticker))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def guardar_posicion(id_inversor: int, ticker: str, cant_actual: float, prec_prom_compra: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_posicion FROM Posicion WHERE id_inversor = ? AND ticker_activo = ?', (id_inversor, ticker))
    row = cursor.fetchone()
    if row:
        cursor.execute('''
            UPDATE Posicion 
            SET cant_actual = ?, prec_prom_compra = ? 
            WHERE id_posicion = ?
        ''', (cant_actual, prec_prom_compra, row[0]))
    else:
        cursor.execute('''
            INSERT INTO Posicion (id_inversor, ticker_activo, cant_actual, prec_prom_compra)
            VALUES (?, ?, ?, ?)
        ''', (id_inversor, ticker, cant_actual, prec_prom_compra))
    conn.commit()
    conn.close()

def eliminar_posicion(id_inversor: int, ticker: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Posicion WHERE id_inversor = ? AND ticker_activo = ?', (id_inversor, ticker))
    conn.commit()
    conn.close()

def registrar_transaccion(id_inversor: int, ticker: str, tipo_operacion: str, cantidad: float, precio_unitario: float, fecha_hora: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Transaccion (id_inversor, ticker_activo, tipo_operacion, cantidad, precio_unitario_ejecucion, fecha_hora)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (id_inversor, ticker, tipo_operacion, cantidad, precio_unitario, fecha_hora))
    conn.commit()
    conn.close()
    
def asegurar_activo(ticker: str, nombre_empresa: str = "N/A", tipo_activo: str = "ACCION"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT ticker FROM ActivoFinanciero WHERE ticker = ?', (ticker,))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO ActivoFinanciero (ticker, nombre_empresa, tipo_activo)
            VALUES (?, ?, ?)
        ''', (ticker, nombre_empresa, tipo_activo))
    conn.commit()
    conn.close()
