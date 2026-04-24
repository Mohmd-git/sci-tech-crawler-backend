import os
import nltk
import requests
import string
import numpy as np

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from nltk.corpus import stopwords

# -----------------------------
# NLTK SETUP
# -----------------------------
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("punkt_tab", quiet=True)

# -----------------------------
# APP SETUP
# -----------------------------
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "https://sci-tech-crawler.vercel.app"
        ]
    }
})

# -----------------------------
# DB CONNECTION
# -----------------------------
MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["knowledge_base"]
collection = db["Summaries"]

print("Connected to MongoDB")

# -----------------------------
# SHORT FORM NORMALIZATION
# -----------------------------
SHORT_FORM_MAP = {
    "ai": "artificial intelligence",
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "rl": "reinforcement learning",
    "llm": "large language models",
    "iot": "internet of things",
    "dbms": "database management system",
    "sql": "structured query language",
    "nosql": "non relational database",
}

def normalize_query(query):
    words = query.lower().split()
    normalized = []

    for w in words:
        if w in SHORT_FORM_MAP:
            normalized.extend(SHORT_FORM_MAP[w].split())
        else:
            normalized.append(w)

    return " ".join(normalized)

# -----------------------------
# PREPROCESS
# -----------------------------
def preprocess_query(query):
    query = query.lower().translate(str.maketrans("", "", string.punctuation))
    tokens = nltk.word_tokenize(query)
    stop_words = set(stopwords.words("english"))
    return [w for w in tokens if w not in stop_words]

# -----------------------------
# FETCH FROM DB
# -----------------------------
def fetch_links_from_db(keywords, max_results=20):
    regex_pattern = "|".join(keywords)

    cursor = collection.find({
        "$or":[
            {"annotations":{"$regex":regex_pattern,"$options":"i"}},
            {"summary":{"$regex":regex_pattern,"$options":"i"}}
        ]
    }).limit(max_results)

    return list(cursor)

# -----------------------------
# DUCKDUCKGO SEARCH
# -----------------------------
def clean_duckduckgo_link(link):
    parsed = urlparse(link)
    if parsed.netloc == "duckduckgo.com":
        query = parse_qs(parsed.query)
        if "uddg" in query:
            return query["uddg"][0]
    return link

def search_duckduckgo(query, max_results=10):
    url = "https://html.duckduckgo.com/html/"
    headers = {"User-Agent":"Mozilla/5.0"}

    response = requests.post(url, data={"q":query}, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    for a in soup.find_all("a", class_="result__a"):
        title = a.get_text(strip=True)
        raw_link = a.get("href")
        link = clean_duckduckgo_link(raw_link)

        results.append({
            "title": title,
            "link": link,
            "summary": title
        })

        if len(results) >= max_results:
            break

    return results

# -----------------------------
# STORE
# -----------------------------
def store_new_links(results):
    for r in results:
        existing = collection.find_one({"link": r["link"]})
        if not existing:
            collection.insert_one(r)

# -----------------------------
# TF-IDF RANKING (ONLY)
# -----------------------------
def tfidf_rank(query, results):
    texts = [r.get("summary","") for r in results]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)

    query_vec = vectorizer.transform([query])

    scores = np.dot(tfidf_matrix, query_vec.T).toarray().flatten()

    for i, r in enumerate(results):
        r["score"] = float(scores[i])

    return sorted(results, key=lambda x: x["score"], reverse=True)

# -----------------------------
# MAIN API
# -----------------------------
@app.route("/rankDocuments", methods=["POST"])
def rank_documents_endpoint():

    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query required"}), 400

    query = normalize_query(query)

    try:
        keywords = preprocess_query(query)

        documents = fetch_links_from_db(keywords)

        if len(documents) < 5:
            web_results = search_duckduckgo(query)
            ranked_web = tfidf_rank(query, web_results)

            store_new_links(ranked_web)

            combined = ranked_web + documents
            final = tfidf_rank(query, combined)

        else:
            final = tfidf_rank(query, documents)

        return jsonify({"results": final[:10]})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal server error"}), 500

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)