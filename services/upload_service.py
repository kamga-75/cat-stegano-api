# =============================================================
#  services/upload_service.py — Logique de sauvegarde fichier
#  Gère la sauvegarde physique des images et l'extraction
#  des métadonnées (taille, dimensions) via Pillow
# =============================================================

import os
import uuid
import mimetypes
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS


def allowed_file(filename):
    """
    Vérifie si l'extension du fichier est autorisée.
    Ex: 'chat.jpg' → True | 'virus.exe' → False
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file):
    """
    Sauvegarde un fichier image dans le dossier uploads/.
    Génère un nom unique avec UUID pour éviter les conflits.
    Retourne un dictionnaire avec :
        - unique_name : nom du fichier sur le serveur
        - filepath    : chemin complet du fichier
        - original_name : nom original sécurisé
        - file_size   : taille en octets
        - mime_type   : type MIME détecté
        - width       : largeur en pixels
        - height      : hauteur en pixels
    Retourne None si la sauvegarde échoue.
    """
    try:
        # Générer un nom unique pour éviter les conflits de noms
        ext         = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        filepath    = os.path.join(UPLOAD_FOLDER, unique_name)

        # Sauvegarder le fichier physiquement dans uploads/
        file.save(filepath)

        # Récupérer les métadonnées du fichier
        file_size = os.path.getsize(filepath)
        mime_type = mimetypes.guess_type(filepath)[0] or 'image/jpeg'

        # Récupérer les dimensions via Pillow
        try:
            from PIL import Image
            with Image.open(filepath) as img:
                width, height = img.size
        except Exception:
            width, height = None, None

        return {
            'unique_name':   unique_name,
            'filepath':      filepath,
            'original_name': secure_filename(file.filename),
            'file_size':     file_size,
            'mime_type':     mime_type,
            'width':         width,
            'height':        height
        }

    except Exception as e:
        print(f"[UPLOAD ERROR] {e}")
        return None


def delete_file(filepath):
    """
    Supprime un fichier physique du dossier uploads/.
    Utilisé en cas d'erreur lors de l'insertion en base.
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"[DELETE FILE ERROR] {e}")
