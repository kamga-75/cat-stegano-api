# =============================================================
#  cat_app.py — Point d'entrée de l'application
#  Lance le serveur Flask et enregistre les routes
#  C'est le seul fichier à exécuter : python cat_app.py
# =============================================================

from flask import Flask
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from routes.images import images_bp
from routes.races import races_bp

# Créer l'application Flask
app = Flask(__name__)

# Configurer le dossier d'upload et la taille maximale des fichiers
app.config['UPLOAD_FOLDER']      = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Enregistrer les blueprints (groupes de routes)
app.register_blueprint(images_bp)  # Routes /api/images
app.register_blueprint(races_bp)   # Routes /api/races


if __name__ == '__main__':
    print("🐱 Cat API démarrée sur http://localhost:5000")
    # debug=True  : redémarrage auto à chaque modification du code
    # host='0.0.0.0' : accessible depuis le réseau local
    # port=5000   : port d'écoute
    app.run(debug=True, host='0.0.0.0', port=5000)
