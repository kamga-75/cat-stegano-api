import os
import uuid
import mimetypes
from flask import Flask, request, jsonify, send_from_directory
import mysql.connector
from mysql.connector import Error
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

DB_CONFIG = {
    'host':     'localhost',
    'port':     3306,
    'user':     'root',
    'password': '',
    'database': 'images_chats',
    'charset':  'utf8mb4'
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB ERROR] {e}")
        return None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_access(image_id, action, req):
    conn = get_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        ip = req.headers.get('X-Forwarded-For', req.remote_addr)
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

@app.route('/api/images', methods=['GET'])
def list_images():
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Erreur DB'}), 500
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
        rows = cursor.fetchall()
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
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/images/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Aucun fichier envoyé'}), 400

    file    = request.files['file']
    race_id = request.form.get('race_id', type=int)
    desc    = request.form.get('description', '')

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Type de fichier non autorisé'}), 400

    ext         = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath    = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(filepath)

    file_size = os.path.getsize(filepath)
    mime_type = mimetypes.guess_type(filepath)[0] or 'image/jpeg'

    try:
        from PIL import Image
        with Image.open(filepath) as img:
            width, height = img.size
    except Exception:
        width, height = None, None

    conn = get_db()
    if not conn:
        os.remove(filepath)
        return jsonify({'success': False, 'error': 'Erreur DB'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cat_images
            (filename, original_name, race_id, file_size, mime_type, width, height, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (unique_name, secure_filename(file.filename), race_id, file_size, mime_type, width, height, desc))
        conn.commit()
        new_id = cursor.lastrowid
        log_access(new_id, 'UPLOAD', request)
        return jsonify({
            'success': True,
            'message': 'Image uploadée avec succès',
            'data': {
                'id':  new_id,
                'url': f"/api/images/{new_id}/file"
            }
        }), 201
    except Error as e:
        os.remove(filepath)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/images/<int:image_id>/file', methods=['GET'])
def serve_image(image_id):
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Erreur DB'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT filename FROM cat_images WHERE id = %s AND is_active = 1",
            (image_id,)
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Image non trouvée'}), 404
        log_access(image_id, 'VIEW', request)
        return send_from_directory(app.config['UPLOAD_FOLDER'], row[0])
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/races', methods=['GET'])
def list_races():
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Erreur DB'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.nom, r.description, COUNT(ci.id) as nb
            FROM races r
            LEFT JOIN cat_images ci ON r.id = ci.race_id AND ci.is_active = 1
            GROUP BY r.id, r.nom, r.description
            ORDER BY r.nom
        """)
        rows = cursor.fetchall()
        return jsonify({'success': True, 'data': [
            {'id': r[0], 'nom': r[1], 'description': r[2], 'nb_images': r[3]}
            for r in rows
        ]})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/images/random', methods=['GET'])
def random_image():
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Erreur DB'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ci.id, ci.filename, r.nom, ci.width, ci.height
            FROM cat_images ci
            LEFT JOIN races r ON ci.race_id = r.id
            WHERE ci.is_active = 1
            ORDER BY RAND() LIMIT 1
        """)
        r = cursor.fetchone()
        if not r:
            return jsonify({'success': False, 'error': 'Aucune image'}), 404
        return jsonify({'success': True, 'data': {
            'id':       r[0],
            'filename': r[1],
            'race':     r[2],
            'width':    r[3],
            'height':   r[4],
            'url':      f"/api/images/{r[0]}/file"
        }})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Erreur DB'}), 500
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
        r = cursor.fetchone()
        if not r:
            return jsonify({'success': False, 'error': 'Image non trouvée'}), 404
        log_access(image_id, 'VIEW', request)
        return jsonify({'success': True, 'data': {
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
        }})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Erreur DB'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE cat_images SET is_active = 0 WHERE id = %s",
            (image_id,)
        )
        conn.commit()
        log_access(image_id, 'DELETE', request)
        return jsonify({'success': True, 'message': 'Image supprimée'})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()
@app.route('/api/images/upload-avec-race', methods=['POST'])
def upload_avec_nouvelle_race():
    file        = request.files.get('file')
    nom_race    = request.form.get('nom_race')
    desc_race   = request.form.get('desc_race', '')
    description = request.form.get('description', '')

    if not file:
        return jsonify({'success': False,
                        'error': 'Aucun fichier'}), 400
    if not nom_race:
        return jsonify({'success': False,
                        'error': 'Nom de race requis'}), 400
    if not allowed_file(file.filename):
        return jsonify({'success': False,
                        'error': 'Type de fichier non autorisé'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'success': False,
                        'error': 'Erreur DB'}), 500
    try:
        cursor = conn.cursor()

        # Vérifier si la race existe déjà
        cursor.execute(
            "SELECT id FROM races WHERE nom = %s",
            (nom_race,)
        )
        race = cursor.fetchone()

        if race:
            race_id = race[0]
        else:
            # Créer la race automatiquement
            cursor.execute("""
                INSERT INTO races (nom, description, statut)
                VALUES (%s, %s, 'en_attente')
            """, (nom_race, desc_race))
            conn.commit()
            race_id = cursor.lastrowid

        # Sauvegarder l'image
        ext         = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        filepath    = os.path.join(app.config['UPLOAD_FOLDER'],
                                   unique_name)
        file.save(filepath)

        file_size = os.path.getsize(filepath)
        mime_type = mimetypes.guess_type(filepath)[0] or 'image/jpeg'

        try:
            from PIL import Image
            with Image.open(filepath) as img:
                width, height = img.size
        except Exception:
            width, height = None, None

        cursor.execute("""
            INSERT INTO cat_images
            (filename, original_name, race_id, file_size,
             mime_type, width, height, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (unique_name, secure_filename(file.filename),
              race_id, file_size, mime_type, width, height,
              description))
        conn.commit()
        new_id = cursor.lastrowid
        log_access(new_id, 'UPLOAD', request)

        return jsonify({
            'success': True,
            'message': 'Image uploadée avec succès !',
            'data': {
                'image_id': new_id,
                'race_id':  race_id,
                'race_nom': nom_race,
                'url':      f"/api/images/{new_id}/file"
            }
        }), 201

    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    print("🐱 Cat API démarrée sur http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
