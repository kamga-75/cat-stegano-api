# =============================================================
#  routes/races.py — Endpoints /api/races
#  Contient toutes les routes liées aux races de chats
# =============================================================

from flask import Blueprint, jsonify
from models.race import get_all_races

# Blueprint pour les routes races
races_bp = Blueprint('races', __name__)


# ── GET /api/races ────────────────────────────────────────────
@races_bp.route('/api/races', methods=['GET'])
def list_races():
    """
    Retourne toutes les races avec le nombre d'images associées.
    Utile pour afficher un filtre par race dans le frontend.
    """
    rows = get_all_races()
    if rows is None:
        return jsonify({'success': False, 'error': 'Erreur DB'}), 500
    return jsonify({'success': True, 'data': [
        {'id': r[0], 'nom': r[1], 'description': r[2], 'nb_images': r[3]}
        for r in rows
    ]})
