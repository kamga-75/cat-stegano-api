# =============================================================
#  models/image.py — Requêtes SQL liées aux images
#  Contient toutes les opérations de base de données
#  pour la table cat_images
# =============================================================

from mysql.connector import Error
from database import get_db


def get_all_images():
    """
    Retourne toutes les images actives avec le nom de leur race.
    Triées par date d'upload (plus récente en premier).
    """
    conn = get_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ci.id, ci.filename, ci.original_name,
                   r.nom, ci.file_size, ci.mime_type,
                   ci.width, ci.height, ci.description, ci.uploaded_at
            FROM cat_images ci
            LEFT JOIN races r ON ci.race_id = r.id
            WHERE ci.is_active = 1
            ORDER BY ci.uploaded_at DESC
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"[MODEL ERROR] {e}")
        return None
    finally:
        conn.close()


def get_image_by_id(image_id):
    """
    Retourne les infos d'une image précise par son ID.
    Retourne None si l'image n'existe pas ou est supprimée.
    """
    conn = get_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ci.id, ci.filename, ci.original_name,
                   r.nom, ci.file_size, ci.mime_type,
                   ci.width, ci.height, ci.description, ci.uploaded_at
            FROM cat_images ci
            LEFT JOIN races r ON ci.race_id = r.id
            WHERE ci.id = %s AND ci.is_active = 1
        """, (image_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"[MODEL ERROR] {e}")
        return None
    finally:
        conn.close()


def get_filename_by_id(image_id):
    """
    Retourne uniquement le nom du fichier d'une image.
    Utilisé pour servir le fichier physique.
    """
    conn = get_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT filename FROM cat_images WHERE id = %s AND is_active = 1",
            (image_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    except Error as e:
        print(f"[MODEL ERROR] {e}")
        return None
    finally:
        conn.close()


def get_random_image():
    """
    Retourne une image aléatoire parmi les images actives.
    Utilisé pour l'affichage initial dans l'app de stéganographie.
    """
    conn = get_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ci.id, ci.filename, r.nom, ci.width, ci.height
            FROM cat_images ci
            LEFT JOIN races r ON ci.race_id = r.id
            WHERE ci.is_active = 1
            ORDER BY RAND() LIMIT 1
        """)
        return cursor.fetchone()
    except Error as e:
        print(f"[MODEL ERROR] {e}")
        return None
    finally:
        conn.close()


def insert_image(filename, original_name, race_id, file_size, mime_type, width, height, description):
    """
    Insère une nouvelle image dans la base de données.
    Retourne l'ID auto-généré par MySQL ou None si échec.
    """
    conn = get_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cat_images
            (filename, original_name, race_id, file_size, mime_type, width, height, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (filename, original_name, race_id, file_size, mime_type, width, height, description))
        conn.commit()
        return cursor.lastrowid  # ID auto-généré par MySQL
    except Error as e:
        print(f"[MODEL ERROR] {e}")
        return None
    finally:
        conn.close()


def soft_delete_image(image_id):
    """
    Supprime une image en mode soft delete (is_active = 0).
    L'image reste dans la base et dans uploads/ pour traçabilité.
    """
    conn = get_db()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE cat_images SET is_active = 0 WHERE id = %s",
            (image_id,)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"[MODEL ERROR] {e}")
        return False
    finally:
        conn.close()
