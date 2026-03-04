# 🐱 Cat Image API

API REST pour gérer les images de chats utilisées dans l'application de stéganographie.

**Stack** : Python + Flask + MySQL (XAMPP)  
**Base URL** : `http://localhost:5000`

---

## ⚙️ Installation

```bash
# 1. Installer les dépendances
pip install flask mysql-connector-python Pillow

# 2. Démarrer XAMPP → MySQL

# 3. Créer la base de données
# → http://localhost/phpmyadmin
# → Créer la base : images_chats
# → Importer : schema.sql

# 4. Lancer l'API
python cat_app.py
```

---

## 🔌 Endpoints

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/images` | Lister toutes les images |
| GET | `/api/images/:id` | Détail d'une image |
| GET | `/api/images/:id/file` | Afficher l'image |
| GET | `/api/images/random` | Image aléatoire |
| GET | `/api/races` | Lister les races |
| POST | `/api/images/upload` | Uploader avec race existante |
| POST | `/api/images/upload-avec-race` | Uploader avec race nouvelle |
| DELETE | `/api/images/:id` | Supprimer une image |

---

## 📖 Exemples JavaScript

```javascript
// Afficher une image
<img src="http://localhost:5000/api/images/1/file" />

// Charger toutes les images
const res = await fetch('http://localhost:5000/api/images');
const { data } = await res.json();

// Image aléatoire
const res = await fetch('http://localhost:5000/api/images/random');
const { data } = await res.json();

// Uploader une image encodée
const formData = new FormData();
formData.append('file', blob, 'chat.png');
formData.append('race_id', 1);
await fetch('http://localhost:5000/api/images/upload', {
    method: 'POST', body: formData
});

// Uploader avec nouvelle race
const formData = new FormData();
formData.append('file', blob, 'chat.png');
formData.append('nom_race', 'Chartreux');
await fetch('http://localhost:5000/api/images/upload-avec-race', {
    method: 'POST', body: formData
});
```

---

## ⚠️ Codes d'erreur

| Code | Signification |
|------|---------------|
| 200 | Succès |
| 201 | Créé avec succès |
| 400 | Requête incorrecte |
| 404 | Ressource introuvable |
| 500 | Erreur serveur |

---

## 📁 Structure

```
cat_api/
├── cat_app.py    ← API Flask
├── schema.sql    ← Base de données
├── README.md     ← Documentation
└── uploads/      ← Images stockées ici
```
