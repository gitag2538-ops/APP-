from flask import Flask, request, jsonify, render_template
import sqlite3
import os

# --- COMPATIBILITÉ NETLIFY ---
# On essaie d'importer serverless_wsgi pour le déploiement
try:
    import serverless_wsgi
except ImportError:
    pass

app = Flask(__name__)

# --- CONFIGURATION DE LA BASE DE DONNÉES ---
# Utilisation de chemins absolus pour éviter les erreurs "File Not Found"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resultats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        x1 REAL,
        x2 REAL,
        P REAL,
        y1 REAL,
        y2 REAL
    )
    """)
    conn.commit()
    conn.close()

# On initialise la base au lancement
init_db()

# --- ROUTES DE L'APPLICATION ---

@app.route('/')
def home():
    # Flask cherchera index.html dans le dossier /templates
    return render_template("index.html")

@app.route('/calcul', methods=['POST'])
def calcul():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Aucune donnée reçue"}), 400

        x1 = float(data.get('x1', 0))
        x2 = float(data.get('x2', 0))

        # Vérification thermodynamique (Somme des fractions molaires = 1)
        if round(x1 + x2, 2) != 1.0:
            return jsonify({"error": "La somme x1 + x2 doit être égale à 1"}), 400

        # Constantes (Exemple Benzène/Toluène)
        P1 = 101.3
        P2 = 40.0

        # Calculs Loi de Raoult
        P = (x1 * P1) + (x2 * P2)
        y1 = (x1 * P1) / P if P != 0 else 0
        y2 = (x2 * P2) / P if P != 0 else 0

        # Sauvegarde dans SQLite
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO resultats (x1, x2, P, y1, y2)
            VALUES (?, ?, ?, ?, ?)
        """, (x1, x2, P, y1, y2))
        conn.commit()
        conn.close()

        return jsonify({
            "Pression_bulle": round(P, 2),
            "y1": round(y1, 3),
            "y2": round(y2, 3),
            "Somme": round(y1 + y2, 3)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/historique')
def historique():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resultats ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- CONFIGURATION POUR NETLIFY (PRODUCTION) ---
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

# --- CONFIGURATION POUR LE TERMINAL (LOCAL) ---
if __name__ == '__main__':
    print("\n" + "="*40)
    print(" APPLICATION THERMODYNAMIQUE LANCÉE")
    print(f" Lien local : http://127.0.0.1:5000")
    print("="*40 + "\n")
    
    # Lancement du serveur local
    app.run(host='127.0.0.1', port=5000, debug=True)