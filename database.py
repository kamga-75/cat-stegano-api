# =============================================================
#  database.py — Gestion de la connexion MySQL
#  Fournit la fonction get_db() utilisée partout dans l'app
# =============================================================

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


def get_db():
    """
    Crée et retourne une connexion MySQL.
    Utilise les paramètres définis dans config.py.
    Retourne None si la connexion échoue.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB ERROR] {e}")
        return None
