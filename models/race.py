# =============================================================
#  models/race.py — Requêtes SQL liées aux races
#  Contient toutes les opérations de base de données
#  pour la table races
# =============================================================

from mysql.connector import Error
from database import get_db


def get_all_races():
    """
    Retourne toutes les races avec le nombre d'images associées.
    Triées par ordre alphabétique.
    """
    conn = get_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.nom, r.description, COUNT(ci.id) as nb
            FROM races r
            LEFT JOIN cat_images ci ON r.id = ci.race_id AND ci.is_active = 1
            GROUP BY r.id, r.nom, r.description
            ORDER BY r.nom
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"[MODEL ERROR] {e}")
        return None
    finally:
        conn.close()


def get_race_by_name(nom):
    """
    Cherche une race par son nom exact.
    Retourne l'ID de la race si elle existe, None sinon.
    Utilisé dans upload-avec-race pour éviter les doublons.
    """
    conn = get_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM races WHERE nom = %s",
            (nom,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    except Error as e:
        print(f"[MODEL ERROR] {e}")
        return None
    finally:
        conn.close()


def insert_race(nom, description):
    """
    Insère une nouvelle race avec statut 'en_attente'.
    La race sera utilisable immédiatement mais devra être
    validée par l'administrateur dans phpMyAdmin.
    Retourne l'ID de la nouvelle race ou None si échec.
    """
    conn = get_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO races (nom, description, statut)
            VALUES (%s, %s, 'en_attente')
        """, (nom, description))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"[MODEL ERROR] {e}")
        return None
    finally:
        conn.close()
