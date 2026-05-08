"""
database/db.py — SQLite database setup and operations for Microscope Calculator
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "microscope.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            image_filename TEXT,
            microscope_type TEXT NOT NULL,
            magnification_factor REAL NOT NULL,
            measured_size REAL NOT NULL,
            real_size REAL NOT NULL,
            input_unit TEXT NOT NULL,
            output_unit TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_user(username: str):
    """Insert a new user or ignore if already exists."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO users (username, created_at) VALUES (?, ?)",
            (username, datetime.now().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def save_calculation(
    username: str,
    image_filename: str,
    microscope_type: str,
    magnification_factor: float,
    measured_size: float,
    real_size: float,
    input_unit: str,
    output_unit: str,
):
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO calculations
              (username, image_filename, microscope_type, magnification_factor,
               measured_size, real_size, input_unit, output_unit, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                image_filename,
                microscope_type,
                magnification_factor,
                measured_size,
                real_size,
                input_unit,
                output_unit,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_calculations(search: str = ""):
    conn = get_connection()
    try:
        if search:
            rows = conn.execute(
                """
                SELECT * FROM calculations
                WHERE username LIKE ? OR microscope_type LIKE ? OR image_filename LIKE ?
                ORDER BY timestamp DESC
                """,
                (f"%{search}%", f"%{search}%", f"%{search}%"),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM calculations ORDER BY timestamp DESC"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_calculation(record_id: int):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM calculations WHERE id = ?", (record_id,))
        conn.commit()
    finally:
        conn.close()


def delete_all_calculations():
    conn = get_connection()
    try:
        conn.execute("DELETE FROM calculations")
        conn.commit()
    finally:
        conn.close()
