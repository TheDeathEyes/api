from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

# On utilise une session pour garder les cookies, ce que le site demande
session = requests.Session()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://anime-sama.to/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

@app.route('/search')
def search():
    query = request.args.get('q', '')
    url = f"https://anime-sama.to/catalogue/?search={query}"
    
    # On fait une première visite pour récupérer les cookies du site
    session.get("https://anime-sama.to/", headers=HEADERS)
    
    # On fait la vraie recherche
    r = session.get(url, headers=HEADERS)
    
    # DEBUG : Voir si on est bloqué
    print(f"Status Code: {r.status_code}")
    
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    
    # Recherche large : on prend tous les liens qui ont un titre et qui pointent vers /catalogue/
    for a in soup.find_all("a", href=True):
        if "/catalogue/" in a['href'] and len(a.text.strip()) > 3:
            # On vérifie que c'est bien un titre d'animé
            if "page" not in a.text.lower() and "recherche" not in a.text.lower():
                results.append({
                    "title": a.text.strip(), 
                    "url": "https://anime-sama.to" + a['href']
                })
    
    # On retire les doublons
    unique_results = {v['title']: v for v in results}.values()
    return jsonify(list(unique_results))

@app.route('/details')
def details():
    url = request.args.get('url', '')
    r = session.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    
    syn = soup.find("p", id="synopsisText")
    return jsonify({
        "synopsis": syn.text.strip() if syn else "Aucun synopsis.",
        "image": soup.find("img", class_="img-fluid")['src'] if soup.find("img", class_="img-fluid") else ""
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
