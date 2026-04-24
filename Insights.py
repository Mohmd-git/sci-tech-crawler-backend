import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import spacy


# Load NLP model
nlp = spacy.load("en_core_web_sm")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    text = " ".join([p.get_text() for p in paragraphs])
    return text[:3000]  # Limit to avoid excessive text

def summarize_text(text):
    return summarizer(text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']

def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text for token in doc if token.is_alpha and token.pos_ in ["NOUN", "PROPN"]]
    return list(set(keywords))[:10]  # Extract top 10 keywords

url = "https://www.geeksforgeeks.org/types-of-blockchain/"  # Replace with your target URL
content = extract_text_from_url(url)
summary = summarize_text(content)
keywords = extract_keywords(content)

print("Summary:", summary)
print("Keywords:", keywords)


#Blockchain technology is a decentralized, distributed ledger system that securely records and verifies transactions across a network of computers. Public blockchains enable open access and decentralization, while private blockchains prioritize security and control. Consortium blockchains serve collaborative networks, and hybrid blockchains combine features of both public and private models.