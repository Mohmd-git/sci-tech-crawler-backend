import os
import nltk
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("punkt_tab", quiet=True)

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

client = MongoClient(MONGO_URI)
db = client["knowledge_base"]
collection = db["Summaries"]

print("Connected to MongoDB")

# -----------------------------
# 🔥 SHORT FORM NORMALIZATION
# -----------------------------
SHORT_FORM_MAP = {

# AI & DATA
"ai": "artificial intelligence",
"ml": "machine learning",
"dl": "deep learning",
"nlp": "natural language processing",
"cv": "computer vision",
"rl": "reinforcement learning",
"llm": "large language models",

# EMERGING TECH
"qc": "quantum computing",
"ar": "augmented reality",
"vr": "virtual reality",
"mr": "mixed reality",

# SYSTEMS / NETWORK
"iot": "internet of things",
"tcp": "transmission control protocol",
"ip": "internet protocol",

# CLOUD / DB
"gcp": "google cloud",
"dbms": "database management system",
"sql": "structured query language",
"nosql": "non relational database",

# PROGRAMMING / DSA
"dsa": "data structures algorithms",
"bst": "binary search tree",
"ll": "linked list",
"ds": "data structures",

# LANGUAGES
"py": "python",
"js": "javascript",
"cpp": "c++",

# MOBILE
"android": "android development",
"ios": "ios development",

# ENERGY
"ev": "electric vehicles"
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
# 🔥 SCI-TECH KEYWORDS
# -----------------------------
SCI_TECH_KEYWORDS = [

# 🔹 CORE CS
"computer science","information technology",
"operating system","distributed systems",
"computer architecture","compiler design",

# 🔹 PROGRAMMING LANGUAGES
"python","java","c","c++","javascript",
"typescript","go","rust","kotlin","swift",
"php","ruby","scala",

# 🔹 PROGRAMMING FUNDAMENTALS
"variables","data types","loops","functions",
"object oriented programming","oops",
"class","inheritance","polymorphism","encapsulation",
"exception handling",

# 🔹 DATA STRUCTURES 🔥
"data structures","array","arrays",
"linked list","stack","queue","deque",
"tree","binary tree","binary search tree",
"heap","priority queue","graph","hashing","hash table",

# 🔹 ALGORITHMS 🔥🔥
"algorithms","sorting algorithms","searching algorithms",
"bubble sort","selection sort","insertion sort",
"merge sort","quick sort","heap sort",
"binary search","linear search",
"graph algorithms","dijkstra","dfs","bfs",
"dynamic programming","greedy algorithms",
"recursion","backtracking",

# 🔹 SOFTWARE DEVELOPMENT
"software engineering","web development",
"app development","mobile applications",
"frontend","backend","full stack",
"api","microservices","devops","git",

# 🔹 DATABASE
"database","sql","nosql","mongodb","mysql",
"postgresql","oracle database",

# 🔹 AI & DATA
"artificial intelligence","machine learning","deep learning",
"neural networks","computer vision",
"natural language processing","reinforcement learning",
"data science","data analytics","data mining",

# 🔹 CLOUD
"cloud computing","aws","azure","google cloud",
"serverless computing","kubernetes","docker",

# 🔹 CYBERSECURITY
"cybersecurity","information security","network security",
"cryptography","encryption","ethical hacking",

# 🔹 NETWORKING
"computer networks","networking",
"network protocols","wireless communication",
"5g","6g",

# 🔹 IOT
"internet of things","embedded systems","smart devices",

# 🔹 BLOCKCHAIN
"blockchain","cryptocurrency","web3","smart contracts",

# 🔹 ROBOTICS
"robotics","automation","autonomous systems",

# 🔹 EMERGING TECH
"quantum computing",
"augmented reality","virtual reality","mixed reality",
"generative ai","large language models",

# 🔹 BIO / SCIENCE
"bioinformatics","computational biology","nanotechnology",

# 🔹 SPACE
"space technology","astronomy","astrophysics",

# 🔹 ELECTRONICS
"semiconductor","vlsi","fpga","asic",

# 🔹 GREEN TECH
"renewable energy","electric vehicles",

# 🔹 TRENDING
"rag","retrieval augmented generation",
"vector database","embeddings","federated learning"
]


# -----------------------------
# Helper functions
# -----------------------------

def serialize_document(doc):
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def preprocess_query(query):
    query = query.lower().translate(str.maketrans("", "", string.punctuation))
    tokens = nltk.word_tokenize(query)
    stop_words = set(stopwords.words("english"))
    return [w for w in tokens if w not in stop_words]


# -----------------------------
# DOMAIN VALIDATION
# -----------------------------

def is_scitech_query(query):
    q = normalize_query(query)

    for keyword in SCI_TECH_KEYWORDS:
        if keyword in q:
            return True

    return False


# -----------------------------
# MongoDB search
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
# DuckDuckGo search
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
# Store new links
# -----------------------------

def store_new_links(results):
    for r in results:
        existing = collection.find_one({"link": r["link"]})

        if not existing:
            collection.insert_one({
                "link": r["link"],
                "annotations": "",
                "summary": r["summary"]
            })


# -----------------------------
# TF-IDF ranking
# -----------------------------

def tfidf_rank(query, results):

    texts = [r.get("summary","") for r in results]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)

    query_vec = vectorizer.transform([query])

    scores = np.dot(tfidf_matrix, query_vec.T).toarray().flatten()

    for i, r in enumerate(results):
        r["tfidf_score"] = float(scores[i])

    return sorted(results, key=lambda x: x["tfidf_score"], reverse=True)


# -----------------------------
# DB Ranking
# -----------------------------

def bm25_ranking(query, documents):

    contents = [doc.get("summary","") for doc in documents]

    vectorizer = TfidfVectorizer().fit(contents)

    query_vector = vectorizer.transform([query])
    doc_vectors = vectorizer.transform(contents)

    scores = np.dot(doc_vectors, query_vector.T).toarray().flatten()

    for i, doc in enumerate(documents):
        doc["bm25_score"] = scores[i]

    return documents


def vector_ranking(query, documents):

    query_embedding = model.encode(query)

    for doc in documents:
        text = doc.get("summary","")
        doc_vector = model.encode(text)

        similarity = np.dot(query_embedding, doc_vector) / (norm(query_embedding) * norm(doc_vector))
        doc["vector_score"] = float(similarity)

    return documents


def reciprocal_rank_fusion(documents, k=60):

    bm25_sorted = sorted(documents, key=lambda x: x.get("bm25_score",0), reverse=True)
    vector_sorted = sorted(documents, key=lambda x: x.get("vector_score",0), reverse=True)

    rrf_scores = defaultdict(float)

    for rank, doc in enumerate(bm25_sorted):
        rrf_scores[str(doc["_id"])] += 1/(k+rank+1)

    for rank, doc in enumerate(vector_sorted):
        rrf_scores[str(doc["_id"])] += 1/(k+rank+1)

    return sorted(documents, key=lambda x: rrf_scores[str(x["_id"])], reverse=True)


# -----------------------------
# MAIN API
# -----------------------------

@app.route("/rankDocuments", methods=["POST"])
def rank_documents_endpoint():

    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query required"}), 400

    # 🔥 Normalize query
    query = normalize_query(query)

    # 🔥 Domain validation
    if not is_scitech_query(query):
        return jsonify({
            "error": "Only Science & Technology queries allowed"
        }), 400

    try:

        keywords = preprocess_query(query)

        documents = fetch_links_from_db(keywords)

        # 🔥 HYBRID SEARCH
        if len(documents) < 5:

            web_results = search_duckduckgo(query)

            ranked_web = tfidf_rank(query, web_results)

            store_new_links(ranked_web)

            combined = ranked_web + documents

            final = tfidf_rank(query, combined)

            serialized = [serialize_document(d) for d in final]

            return jsonify({"results": serialized[:10]})

        # 🔥 DB ONLY
        bm25 = bm25_ranking(query, documents)
        vec = vector_ranking(query, bm25)
        final = reciprocal_rank_fusion(vec)

        serialized = [serialize_document(d) for d in final]

        return jsonify({"results": serialized[:10]})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal server error"}), 500


# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)