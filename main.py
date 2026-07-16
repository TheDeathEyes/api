from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

@app.route('/search')
def search():
    query = request.args.get('q', '')
    url = f"https://anime-sama.to/catalogue/?search={query}"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for card in soup.select(".cardAnime, .anime-card, .catalog-card"):
        link = card.find("a")
        title = card.find(["h1", "h2", "h3", "p"])
        if link and title:
            results.append({"title": title.text.strip(), "url": "https://anime-sama.to" + link['href']})
    return jsonify(results)

@app.route('/details')
def details():
    url = request.args.get('url', '')
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Image et Synopsis
    img = soup.find("img", class_="img-fluid")
    syn = soup.find("p", id="synopsisText")
    
    # Lecteurs (extraction simplifiée)
    versions = {"PRINCIPALE": {}}
    js_url = url.rstrip('/') + "/episodes.js"
    js_res = requests.get(js_url, headers=HEADERS)
    if js_res.status_code == 200:
        matches = re.findall(r"var\s+(eps\d+)\s*=\s*\[(.*?)\]", js_res.text)
        for var_name, content in matches:
            links = re.findall(r'"(https?://.*?)"', content)
            versions["PRINCIPALE"][f"Lecteur {var_name.replace('eps', '')}"] = links
            
    return jsonify({
        "image": img['src'] if img else "",
        "synopsis": syn.text.strip() if syn else "",
        "versions": versions
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
