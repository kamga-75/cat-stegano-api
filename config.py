# =============================================================
#  config.py — Configuration centrale de l'application
#  Contient tous les paramètres : DB, upload, sécurité
# =============================================================

import os

# ── Dossier de stockage des images ────────────────────────────
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

# Extensions de fichiers autorisées
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Taille maximale d'un fichier : 10 MB
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

# ── Configuration MySQL (XAMPP) ───────────────────────────────
DB_CONFIG = {
    'host':     'localhost',       # MySQL tourne en local
    'port':     3306,              # Port par défaut MySQL
    'user':     'root',            # Utilisateur XAMPP par défaut
    'password': '',                # Vide par défaut sur XAMPP
    'database': 'images_chats',    # Nom de la base de données
    'charset':  'utf8mb4'          # Support accents et emojis
}
