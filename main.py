from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

session = requests.Session()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://anime-sama.to/"
}

@app.route('/search')
def search():
    query = request.args.get('q', '')
    url = f"https://anime-sama.to/catalogue/?search={query}"
    r = session.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for a in soup.find_all("a", href=True):
        if "/catalogue/" in a['href'] and len(a.text.strip()) > 3:
            # Sécurisation : construire l'URL proprement
            link = a['href']
            if not link.startswith("http"):
                link = "https://anime-sama.to" + link
            elif "anime-sama.to" not in link:
                continue # Ignore liens externes
                
            results.append({"title": a.text.strip(), "url": link})
    return jsonify(list({v['title']:v for v in results}.values()))

@app.route('/details')
def details():
    url = request.args.get('url', '')
    if not url.startswith("http"): return jsonify({"error": "URL invalide"}), 400
    
    r = session.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    
    img = soup.find("img", class_="img-fluid")
    syn = soup.find("p", id="synopsisText")
    lecteurs = [iframe['src'] for iframe in soup.find_all("iframe", src=True)]
    
    return jsonify({
        "image": img['src'] if img else "",
        "synopsis": syn.text.strip() if syn else "Aucun synopsis.",
        "lecteurs": lecteurs
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
