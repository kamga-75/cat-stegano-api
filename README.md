# 🐱 Cat Image API — Documentation Complète

API REST pour gérer une base de données d'images de chats, construite avec **Flask + MySQL**.

---

## 📁 Structure du projet

```
cat_api/
├── app.py              ← Application Flask principale (API)
├── schema.sql          ← Script de création de la base de données
├── requirements.txt    ← Dépendances Python
├── uploads/            ← Dossier de stockage des images
└── README.md           ← Cette documentation
```

---

## ⚙️ Installation & Configuration

### 1. Prérequis
- Python 3.8+
- MySQL 5.7+ ou MariaDB 10.3+

### 2. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

### 3. Créer la base de données MySQL
```bash
mysql -u root -p < schema.sql
```
Cela va créer automatiquement la base `cat_images_db` avec toutes les tables et les races pré-remplies.

### 4. Configurer la connexion MySQL
Dans `app.py`, modifie le bloc `DB_CONFIG` :
```python
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',           # ← ton utilisateur MySQL
    'password': 'ton_mot_de_passe', # ← ton mot de passe
    'database': 'cat_images_db'
}
```

### 5. Lancer l'API
```bash
python app.py
```
L'API est accessible sur : **http://localhost:5000**

---

## 🔌 Endpoints de l'API

### 📋 Images

| Méthode | URL | Description |
|---------|-----|-------------|
| `GET` | `/api/images` | Lister toutes les images |
| `GET` | `/api/images/<id>` | Détail d'une image |
| `GET` | `/api/images/<id>/file` | Afficher/télécharger l'image |
| `GET` | `/api/images/random` | Image aléatoire |
| `POST` | `/api/images/upload` | Uploader une image |
| `PUT` | `/api/images/<id>` | Modifier les infos d'une image |
| `DELETE` | `/api/images/<id>` | Supprimer une image |

### 🐾 Races

| Méthode | URL | Description |
|---------|-----|-------------|
| `GET` | `/api/races` | Lister toutes les races + nombre d'images |

### 📊 Statistiques

| Méthode | URL | Description |
|---------|-----|-------------|
| `GET` | `/api/stats` | Statistiques générales |

---

## 📖 Exemples d'utilisation

### Lister toutes les images
```http
GET /api/images
```
**Réponse :**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "filename": "abc123.jpg",
      "original_name": "mon_chat.jpg",
      "race_id": 1,
      "race_nom": "Siamois",
      "file_size": 204800,
      "mime_type": "image/jpeg",
      "width": 1920,
      "height": 1080,
      "description": "Mon chat siamois sur le canapé",
      "uploaded_at": "2024-01-15T14:30:00",
      "url": "/api/images/1/file"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "total_pages": 3
  }
}
```

### Filtrer par race (ex: race_id=2)
```http
GET /api/images?race_id=2&page=1&limit=10
```

### Uploader une image
```http
POST /api/images/upload
Content-Type: multipart/form-data

file=<fichier_image>
race_id=3
description=Chat Bengal au jardin
```

### Obtenir une image aléatoire
```http
GET /api/images/random
GET /api/images/random?race_id=5  ← aléatoire parmi les Bengal
```

### Modifier les infos d'une image
```http
PUT /api/images/1
Content-Type: application/json

{
  "race_id": 4,
  "description": "Nouvelle description"
}
```

### Statistiques
```http
GET /api/stats
```
```json
{
  "success": true,
  "data": {
    "total_images": 45,
    "total_size_mb": 128.5,
    "by_race": [
      {"race": "Maine Coon", "count": 12},
      {"race": "Siamois",    "count": 8}
    ],
    "access_7_days": 342
  }
}
```

---

## 🗃️ Structure de la base de données

### Table `races`
| Colonne | Type | Description |
|---------|------|-------------|
| id | INT | Identifiant unique |
| nom | VARCHAR(100) | Nom de la race (ex: "Siamois") |
| description | TEXT | Description de la race |

### Table `cat_images`
| Colonne | Type | Description |
|---------|------|-------------|
| id | INT | Identifiant unique |
| filename | VARCHAR(255) | Nom unique du fichier sur le serveur |
| original_name | VARCHAR(255) | Nom original du fichier uploadé |
| race_id | INT | Référence vers la race |
| file_size | INT | Taille en octets |
| mime_type | VARCHAR(50) | Type MIME (image/jpeg, image/png...) |
| width / height | INT | Dimensions en pixels |
| description | TEXT | Description libre |
| is_active | TINYINT | 1=visible, 0=supprimée (soft delete) |
| uploaded_at | DATETIME | Date d'upload |

### Table `access_logs`
| Colonne | Type | Description |
|---------|------|-------------|
| id | BIGINT | Identifiant unique |
| image_id | INT | Image concernée (peut être NULL) |
| action | ENUM | VIEW, UPLOAD, DELETE, LIST |
| ip_address | VARCHAR(45) | Adresse IP du client |
| user_agent | VARCHAR(255) | Navigateur/client utilisé |
| accessed_at | DATETIME | Horodatage |

---

## 🔒 Sécurité

- **Noms de fichiers** : générés automatiquement avec UUID (pas de conflit, pas d'injection)
- **Types de fichiers** : seuls PNG, JPG, JPEG, GIF, WEBP sont acceptés
- **Taille maximale** : 10 MB par fichier
- **Soft delete** : les images "supprimées" restent sur le serveur (is_active=0) pour traçabilité
- **Logs d'accès** : chaque action est enregistrée avec IP et timestamp

---

## 🚀 Intégration avec ton app de stéganographie

Dans ton app frontend, tu peux :
1. Charger la liste des images de chats via `GET /api/images`
2. Afficher les images avec `GET /api/images/<id>/file`
3. Après encodage, uploader l'image résultante via `POST /api/images/upload`

```javascript
// Exemple : charger les images de chats disponibles
const response = await fetch('http://localhost:5000/api/images?limit=50');
const { data } = await response.json();

// Afficher chaque image
data.forEach(img => {
  const el = document.createElement('img');
  el.src = `http://localhost:5000${img.url}`;
  document.body.appendChild(el);
});
```
