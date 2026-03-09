# =============================================================
#  routes/images.py — Endpoints /api/images
#  Contient toutes les routes liées aux images de chats
# =============================================================

from flask import Blueprint, request, jsonify, send_from_directory
from config import UPLOAD_FOLDER
from models.image import (
    get_all_images, get_image_by_id, get_filename_by_id,
    get_random_image, insert_image, soft_delete_image
)
from models.race import get_race_by_name, insert_race
from services.upload_service import allowed_file, save_file, delete_file
from services.log_service import log_access

# Blueprint = groupe de routes Flask
# Permet d'organiser les routes par thème (images, races...)
images_bp = Blueprint('images', __name__)


# ── GET /api/images ───────────────────────────────────────────
@images_bp.route('/api/images', methods=['GET'])
def list_images():
    """Retourne toutes les images actives avec le nom de leur race."""
    rows = get_all_images()
    if rows is None:
        return jsonify({'success': False, 'error': 'Erreur DB'}), 500
    images = [{
        'id':            r[0],
        'filename':      r[1],
        'original_name': r[2],
        'race':          r[3],
        'file_size':     r[4],
        'mime_type':     r[5],
        'width':         r[6],
        'height':        r[7],
        'description':   r[8],
        'uploaded_at':   str(r[9]),
        'url':           f"/api/images/{r[0]}/file"
    } for r in rows]
    log_access(None, 'LIST', request)
    return jsonify({'success': True, 'data': images})


# ── GET /api/images/random ────────────────────────────────────
@images_bp.route('/api/images/random', methods=['GET'])
def random_image():
    """
    Retourne une image aléatoire.
    Utile pour l'affichage initial dans l'app de stéganographie
    ou pour un bouton 'Autre image'.
    """
    r = get_random_image()
    if not r:
        return jsonify({'success': False, 'error': 'Aucune image'}), 404
    return jsonify({'success': True, 'data': {
        'id': r[0], 'filename': r[1], 'race': r[2],
        'width': r[3], 'height': r[4],
        'url': f"/api/images/{r[0]}/file"
    }})


# ── GET /api/images/<id> ──────────────────────────────────────
@images_bp.route('/api/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """
    Retourne toutes les infos d'une image précise.
    Utile pour retrouver une image par son ID après décodage.
    """
    r = get_image_by_id(image_id)
    if not r:
        return jsonify({'success': False, 'error': 'Image non trouvée'}), 404
    log_access(image_id, 'VIEW', request)
    return jsonify({'success': True, 'data': {
        'id': r[0], 'filename': r[1], 'original_name': r[2],
        'race': r[3], 'file_size': r[4], 'mime_type': r[5],
        'width': r[6], 'height': r[7], 'description': r[8],
        'uploaded_at': str(r[9]), 'url': f"/api/images/{r[0]}/file"
    }})


# ── GET /api/images/<id>/file ─────────────────────────────────
@images_bp.route('/api/images/<int:image_id>/file', methods=['GET'])
def serve_image(image_id):
    """
    Retourne le fichier image physique pour affichage direct.
    Exemple d'utilisation : <img src="/api/images/1/file" />
    """
    filename = get_filename_by_id(image_id)
    if not filename:
        return jsonify({'error': 'Image non trouvée'}), 404
    log_access(image_id, 'VIEW', request)
    return send_from_directory(UPLOAD_FOLDER, filename)


# ── POST /api/images/upload ───────────────────────────────────
@images_bp.route('/api/images/upload', methods=['POST'])
def upload_image():
    """
    Uploade une image avec une race existante.
    form-data : file (obligatoire), race_id, description
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Aucun fichier envoyé'}), 400

    file    = request.files['file']
    race_id = request.form.get('race_id', type=int)
    desc    = request.form.get('description', '')

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Type de fichier non autorisé'}), 400

    # Sauvegarder le fichier et récupérer ses métadonnées
    file_data = save_file(file)
    if not file_data:
        return jsonify({'success': False, 'error': 'Erreur lors de la sauvegarde'}), 500

    # Insérer dans MySQL
    new_id = insert_image(
        file_data['unique_name'], file_data['original_name'],
        race_id, file_data['file_size'], file_data['mime_type'],
        file_data['width'], file_data['height'], desc
    )

    if not new_id:
        delete_file(file_data['filepath'])  # Supprimer si DB échoue
        return jsonify({'success': False, 'error': 'Erreur DB'}), 500

    log_access(new_id, 'UPLOAD', request)
    return jsonify({
        'success': True,
        'message': 'Image uploadée avec succès',
        'data': {'id': new_id, 'url': f"/api/images/{new_id}/file"}
    }), 201


# ── POST /api/images/upload-avec-race ────────────────────────
@images_bp.route('/api/images/upload-avec-race', methods=['POST'])
def upload_avec_nouvelle_race():
    """
    Uploade une image avec une race existante ou nouvelle.
    Si la race n'existe pas → créée automatiquement (statut: en_attente).
    Cas d'usage : message urgent avec une race non encore dans la base.
    form-data : file, nom_race (obligatoires), desc_race, description
    """
    file        = request.files.get('file')
    nom_race    = request.form.get('nom_race')
    desc_race   = request.form.get('desc_race', '')
    description = request.form.get('description', '')

    if not file:
        return jsonify({'success': False, 'error': 'Aucun fichier'}), 400
    if not nom_race:
        return jsonify({'success': False, 'error': 'Nom de race requis'}), 400
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Type de fichier non autorisé'}), 400

    # Vérifier si la race existe, sinon la créer
    race_id = get_race_by_name(nom_race)
    if not race_id:
        race_id = insert_race(nom_race, desc_race)
    if not race_id:
        return jsonify({'success': False, 'error': 'Erreur création race'}), 500

    # Sauvegarder le fichier
    file_data = save_file(file)
    if not file_data:
        return jsonify({'success': False, 'error': 'Erreur sauvegarde fichier'}), 500

    # Insérer dans MySQL
    new_id = insert_image(
        file_data['unique_name'], file_data['original_name'],
        race_id, file_data['file_size'], file_data['mime_type'],
        file_data['width'], file_data['height'], description
    )

    if not new_id:
        delete_file(file_data['filepath'])
        return jsonify({'success': False, 'error': 'Erreur DB'}), 500

    log_access(new_id, 'UPLOAD', request)
    return jsonify({
        'success': True,
        'message': 'Image uploadée avec succès !',
        'data': {
            'image_id': new_id, 'race_id': race_id,
            'race_nom': nom_race, 'url': f"/api/images/{new_id}/file"
        }
    }), 201


# ── DELETE /api/images/<id> ───────────────────────────────────
@images_bp.route('/api/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """
    Soft delete : is_active = 0 sans supprimer le fichier physique.
    Permet de garder la traçabilité et de restaurer si besoin.
    """
    success = soft_delete_image(image_id)
    if not success:
        return jsonify({'success': False, 'error': 'Erreur DB'}), 500
    log_access(image_id, 'DELETE', request)
    return jsonify({'success': True, 'message': 'Image supprimée'})
