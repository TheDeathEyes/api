from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, re
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)
session = requests.Session()
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

@app.route('/search')
def search():
    query = request.args.get('q', '')
    r = session.get(f"https://anime-sama.to/catalogue/?search={query}", headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    # Recherche les liens d'animés
    for a in soup.find_all("a", href=True):
        if "/catalogue/" in a['href'] and len(a.text.strip()) > 3:
            link = a['href'] if a['href'].startswith("http") else "https://anime-sama.to" + a['href']
            results.append({"title": a.text.strip(), "url": link})
    return jsonify(list({v['title']:v for v in results}.values()))

@app.route('/episodes')
def episodes():
    url_base = request.args.get('url', '').rstrip('/')
    # 1. On récupère la page principale pour trouver les liens des saisons/langues
    r = session.get(url_base, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Récupérer tous les liens de sous-catégories (vf, vostfr, saison...)
    liens_saisons = []
    for a in soup.find_all("a", href=True):
        if any(x in a['href'] for x in ["/vostfr/", "/vf/", "/saison"]):
            full_link = a['href'] if a['href'].startswith("http") else "https://anime-sama.to" + a['href']
            liens_saisons.append(full_link)
    
    liens_saisons = list(set(liens_saisons)) # Suppression des doublons
    
    # 2. Pour chaque saison, on cherche le fichier episodes.js
    tous_les_lecteurs = []
    for lien in liens_saisons:
        r_saison = session.get(lien, headers=HEADERS)
        # Chercher le script qui contient episodes.js
        scripts = BeautifulSoup(r_saison.text, "html.parser").find_all("script", src=True)
        for s in scripts:
            if "episodes.js" in s['src']:
                js_url = s['src'] if s['src'].startswith("http") else lien.rstrip('/') + "/" + s['src'].lstrip('/')
                js_res = session.get(js_url, headers=HEADERS)
                if js_res.status_code == 200:
                    blocs = re.findall(r"var\s+(eps\d+)\s*=\s*\[([\s\S]*?)\]", js_res.text)
                    for nom_var, bloc in blocs:
                        liens = re.findall(r"['\"](https?://[^\s'\"`><]+)['\"]", bloc)
                        if liens:
                            tous_les_lecteurs.append({"title": f"Lecteur {nom_var.replace('eps','')}", "link": liens[0]})
    
    return jsonify(tous_les_lecteurs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
