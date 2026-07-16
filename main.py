from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import os

app = Flask(__name__)
# Autorise les appels depuis n'importe quelle origine
CORS(app, resources={r"/*": {"origins": "*"}})

BASE_URL = "https://anime-sama.to"
# Headers complets pour éviter le blocage 404/403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://anime-sama.to/",
    "Origin": "https://anime-sama.to",
    "Connection": "keep-alive"
}

session = requests.Session()
session.headers.update(HEADERS)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query: return jsonify([])
    try:
        # On appelle l'API de recherche directement
        r = session.get(f"{BASE_URL}/api/search.php?q={query}", timeout=10)
        return r.text, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/details')
def details():
    anime_url = request.args.get('url', '').rstrip('/')
    try:
        # Récupération de la page principale
        r = session.get(anime_url, timeout=10)
        page_html = r.text
    except:
        return jsonify({"synopsis": "", "versions": {}})

    # Extraction du synopsis
    synopsis = "Aucun synopsis disponible."
    m_syn = re.search(r'<p id="synopsisText"[^>]*>([\s\S]*?)</p>', page_html, re.IGNORECASE)
    if m_syn:
        synopsis = re.sub('<[^<]+?>', '', m_syn.group(1)).strip()

    # Extraction des épisodes
    variantes = ["/vostfr/episodes.js", "/vf/episodes.js", "/episodes.js"]
    donnees_versions = {}

    for sous_url in variantes:
        try:
            js_res = session.get(anime_url + sous_url, timeout=5)
            js_content = js_res.text
        except:
            continue

        if "eps" in js_content:
            nom_version = sous_url.replace("/episodes.js", "").strip("/").upper()
            if not nom_version: nom_version = "PRINCIPALE"
            
            if nom_version not in donnees_versions:
                donnees_versions[nom_version] = {}

            matches = re.findall(r'var\s+(eps\d+)\s*=\s*\[([\s\S]*?)\]', js_content)
            for var_name, content_array in matches:
                liens = re.findall(r'[\'"](https?://[^\s\'"`><]+)[\'"]', content_array)
                if liens:
                    liens_corriges = [l.replace('vidmoly.to', 'vidmoly.biz') for l in liens]
                    num_lecteur = var_name.replace('eps', '')
                    nom_hebergeur = f"Lecteur {num_lecteur}"
                    donnees_versions[nom_version][nom_hebergeur] = liens_corriges

    return jsonify({"synopsis": synopsis, "versions": donnees_versions})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
