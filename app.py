from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import joblib
import socket
import tldextract

app = Flask(__name__)
CORS(app)

# Load your trained model
model = joblib.load("fraud_model.pkl")

# Helper: check if domain is an IP
def is_ip(domain):
    try:
        socket.inet_aton(domain)
        return 1
    except:
        return 0

# Feature extraction based on your dataset
def extract_features(url):
    try:
        res = requests.get(url, timeout=5)
        html = res.text
    except:
        html = ""
    
    soup = BeautifulSoup(html, "html.parser")
    ext = tldextract.extract(url)
    domain = f"{ext.subdomain}.{ext.domain}.{ext.suffix}".strip('.')

    # Features (match your dataset's columns as closely as possible)
    features = {
        "URLLength": len(url),
        "DomainLength": len(domain),
        "IsDomainIP": is_ip(domain),
        "TLD": ext.suffix,
        "URLSimilarityIndex": 100.0,  # Placeholder unless using similarity logic
        "CharContinuationRate": len(url) / (url.count('/') + 1),
        "HasCopyrightInfo": int("copyright" in html.lower()),
        "NoOfImage": len(soup.find_all("img")),
        "NoOfCSS": len(soup.find_all("link", {"rel": "stylesheet"})),
        "NoOfJS": len(soup.find_all("script")),
        "NoOfSelfRef": len([a for a in soup.find_all("a", href=True) if domain in a["href"]]),
        "NoOfEmptyRef": len([a for a in soup.find_all("a", href=True) if a["href"] in ["#", ""]]),
        "NoOfExternalRef": len([a for a in soup.find_all("a", href=True) if domain not in a["href"]]),
        "Pay": int("pay" in url.lower()),
        "Crypto": int("bitcoin" in html.lower() or "crypto" in html.lower()),
    }

    return features

@app.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    url = data.get("url", "")

    if not url:
        return jsonify({"error": "URL missing"}), 400

    try:
        features_dict = extract_features(url)

        # You must match model input column order
        model_features = [
            features_dict["URLLength"],
            features_dict["DomainLength"],
            features_dict["IsDomainIP"],
            features_dict["URLSimilarityIndex"],
            features_dict["CharContinuationRate"],
            features_dict["HasCopyrightInfo"],
            features_dict["NoOfImage"],
            features_dict["NoOfCSS"],
            features_dict["NoOfJS"],
            features_dict["NoOfSelfRef"],
            features_dict["NoOfEmptyRef"],
            features_dict["NoOfExternalRef"],
            features_dict["Pay"],
            features_dict["Crypto"]
        ]

        prediction = model.predict([model_features])[0]

        return jsonify({
            "url": url,
            "fraudulent": bool(prediction),
            "message": "Dangerous" if prediction else "Safe"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
    
