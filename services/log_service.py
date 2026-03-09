# =============================================================
#  services/log_service.py — Gestion des logs d'accès
#  Enregistre chaque action dans la table access_logs
#  pour assurer la traçabilité des opérations
# =============================================================

from mysql.connector import Error
from database import get_db


def log_access(image_id, action, req):
    """
    Enregistre une action dans la table access_logs.
    Paramètres :
        image_id : ID de l'image concernée (None pour les listes)
        action   : 'VIEW', 'UPLOAD', 'DELETE', 'LIST'
        req      : objet request Flask (IP + navigateur)
    """
    conn = get_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        # Récupérer l'adresse IP (gère les proxies avec X-Forwarded-For)
        ip = req.headers.get('X-Forwarded-For', req.remote_addr)
        # Récupérer le navigateur utilisé (limité à 255 caractères)
        ua = req.headers.get('User-Agent', '')[:255]
        cursor.execute(
            "INSERT INTO access_logs (image_id, action, ip_address, user_agent) VALUES (%s, %s, %s, %s)",
            (image_id, action, ip, ua)
        )
        conn.commit()
    except Error as e:
        print(f"[LOG ERROR] {e}")
    finally:
        conn.close()
