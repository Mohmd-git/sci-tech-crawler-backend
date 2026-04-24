# # import hashlib
# # import requests
# # from bs4 import BeautifulSoup
# # from collections import Counter
# # import re
# # import os
# # from langdetect import detect
# # from urllib.parse import urljoin

# # # Initialize a queue (set) to keep track of visited URLs
# # queue = set()

# # def hash_url(url):
# #     """Hash the URL using SHA-256."""
# #     return hashlib.sha256(url.encode()).hexdigest()

# # def fetch_page_content(url):
# #     """Fetch the content of a webpage."""
# #     try:
# #         response = requests.get(url)
# #         response.raise_for_status()  # Raise an exception for HTTP errors
# #         return response.text
# #     except requests.RequestException as e:
# #         print(f"Error fetching {url}: {e}")
# #         return None

# # def extract_text(content):
# #     """Extract the text content from a webpage."""
# #     soup = BeautifulSoup(content, "html.parser")
# #     return soup.get_text(separator="\n")

# # def clean_and_tokenize(text):
# #     """Clean text and tokenize into words."""
# #     words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())  # Keep words with at least 3 characters
# #     return words

# # def filter_technology_words(words):
# #     """Filter words based on technology-related keywords."""
# #     tech_keywords = {
# #         'cybersecurity', 'network', 'encryption', 'data', 'technology', 'science', 'cloud',
# #         'software', 'hardware', 'ai', 'machine', 'learning', 'robotics', 'automation',
# #         'algorithm', 'quantum', 'computing', 'database', 'programming', 'development',
# #         'engineering', 'internet', 'digital', 'blockchain', 'virtual', 'reality', 'iot',
# #         'innovation', 'biotech', 'nanotechnology', 'genomics'
# #     }
# #     return [word for word in words if word in tech_keywords]

# # def extract_hyperlinks(url, content):
# #     """Extract all hyperlinks from a webpage."""
# #     soup = BeautifulSoup(content, "html.parser")
# #     hyperlinks = set()
# #     for link in soup.find_all("a", href=True):
# #         href = link.get("href")
# #         full_url = urljoin(url, href)
# #         if full_url not in queue:  # Only add links that are not already visited
# #             hyperlinks.add(full_url)
# #     return hyperlinks

# # def save_content_to_file(url, content, directory="webpages"):
# #     """Save the webpage content to a text file."""
# #     if not os.path.exists(directory):
# #         os.makedirs(directory)
# #     filename = hash_url(url) + ".txt"
# #     file_path = os.path.join(directory, filename)
# #     with open(file_path, "w", encoding="utf-8") as file:
# #         file.write(content)

# # def crawl(urls, top_n=10):
# #     """Crawl each URL, fetch content, and extract hyperlinks."""
# #     to_crawl = set(urls)  # URLs to crawl initially
# #     while to_crawl:
# #         url = to_crawl.pop()
# #         hashed_url = hash_url(url)

# #         if hashed_url in queue:
# #             continue

# #         print(f"Crawling: {url}")
# #         queue.add(hashed_url)

# #         content = fetch_page_content(url)
# #         if not content:
# #             continue

# #         text = extract_text(content)

# #         # Detect language and filter English-only pages
# #         try:
# #             if detect(text) != 'en':
# #                 print(f"Skipping non-English page: {url}")
# #                 continue
# #         except Exception as e:
# #             print(f"Language detection failed for {url}: {e}")
# #             continue

# #         # Save the page content
# #         save_content_to_file(url, text)

# #         # Tokenize and rank technology-related words
# #         words = clean_and_tokenize(text)
# #         tech_words = filter_technology_words(words)
# #         word_counts = Counter(tech_words)

# #         print(f"Top {top_n} technology-related words from {url}:")
# #         for word, count in word_counts.most_common(top_n):
# #             print(f"{word}: {count}")

# #         # Extract and process hyperlinks
# #         hyperlinks = extract_hyperlinks(url, content)
# #         filtered_links = filter_science_technology_links(hyperlinks)
# #         print(f"Found {len(filtered_links)} science/technology-related hyperlinks on {url}.")

# #         # Add filtered links to the crawl queue
# #         to_crawl.update(filtered_links)

# # def filter_science_technology_links(links):
# #     """Filter hyperlinks containing science/technology-related keywords."""
# #     science_technology_keywords = [
# #         'science', 'technology', 'cybersecurity', 'data', 'engineering', 'computing',
# #         'robotics', 'ai', 'machine-learning', 'blockchain', 'iot', 'innovation',
# #         'biotech', 'quantum', 'automation', 'digital', 'genomics', 'nanotechnology'
# #     ]
# #     filtered_links = []
# #     for link in links:
# #         for keyword in science_technology_keywords:
# #             if keyword in link.lower():
# #                 filtered_links.append(link)
# #                 break
# #     return filtered_links

# # if __name__ == "__main__":
# #     # Example seed URLs
# #     seed_urls = [
# #         "https://www.cisco.com/site/us/en/learn/topics/security/what-is-cybersecurity.html"
# #     ]

# #     # Start the crawling process
# #     crawl(seed_urls)

# import requests
# from bs4 import BeautifulSoup
# from sklearn.feature_extraction.text import TfidfVectorizer
# import hashlib
# from urllib.parse import urljoin
# import nltk
# from nltk.corpus import stopwords
# import string
# from collections import Counter

# # Ensure NLTK resources are available
# nltk.download('punkt')
# nltk.download('stopwords')

# # Hash a URL using SHA-256 for unique identification
# def hash_url(url):
#     return hashlib.sha256(url.encode()).hexdigest()

# # Fetch content from a URL
# def fetch_page_content(url):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         return response.text
#     except requests.RequestException as e:
#         print(f"Error fetching {url}: {e}")
#         return None

# # Extract text content from the webpage
# def extract_text(content):
#     soup = BeautifulSoup(content, "html.parser")
#     return ' '.join(p.get_text() for p in soup.find_all('p'))

# # Preprocess text by removing punctuation, numbers, and stopwords
# def preprocess_text(text):
#     text = text.lower()
#     text = text.translate(str.maketrans('', '', string.punctuation))
#     text = ''.join([char for char in text if not char.isdigit()])

#     tokens = nltk.word_tokenize(text)
#     stop_words = set(stopwords.words('english'))
#     tokens = [word for word in tokens if word not in stop_words]

#     return ' '.join(tokens)

# # Calculate TF-IDF values for the given text
# def calculate_tfidf(text):
#     vectorizer = TfidfVectorizer()
#     tfidf_matrix = vectorizer.fit_transform([text])
#     feature_names = vectorizer.get_feature_names_out()
#     tfidf_scores = tfidf_matrix.toarray().flatten()

#     tfidf_dict = dict(zip(feature_names, tfidf_scores))
#     return tfidf_dict

# # Sort TF-IDF results in descending order
# def sort_tfidf(tfidf_dict):
#     sorted_tfidf = sorted(tfidf_dict.items(), key=lambda item: item[1], reverse=True)
#     return sorted_tfidf

# # Get top N keywords based on TF-IDF scores
# def get_top_keywords(sorted_tfidf, top_n=10):
#     return sorted_tfidf[:top_n]

# # Extract hyperlinks from a webpage
# def extract_hyperlinks(url, content):
#     soup = BeautifulSoup(content, "html.parser")
#     hyperlinks = set()
#     for link in soup.find_all("a", href=True):
#         full_url = urljoin(url, link.get("href"))
#         hyperlinks.add(full_url)
#     return hyperlinks

# # Main crawling function
# def crawl_and_analyze(urls, top_n=10):
#     queue = set(urls)
#     visited = set()

#     while queue:
#         url = queue.pop()
#         if url in visited:
#             continue

#         print(f"Crawling: {url}")
#         visited.add(url)

#         content = fetch_page_content(url)
#         if not content:
#             continue

#         text = extract_text(content)
#         preprocessed_text = preprocess_text(text)

#         tfidf_dict = calculate_tfidf(preprocessed_text)
#         sorted_tfidf = sort_tfidf(tfidf_dict)
#         top_keywords = get_top_keywords(sorted_tfidf, top_n=top_n)

#         print(f"Top {top_n} keywords from {url}:")
#         for keyword, score in top_keywords:
#             print(f"{keyword}: {score:.4f}")

#         hyperlinks = extract_hyperlinks(url, content)
#         queue.update(hyperlinks - visited)

# # Example usage
# if __name__ == "__main__":
#   seed_urls = [
#     "https://www.ibm.com/think/topics/artificial-intelligence",
#     "https://cloud.google.com/learn/what-is-artificial-intelligence",
#     "https://www.geeksforgeeks.org/what-is-ai/",
#     "https://www.geeksforgeeks.org/machine-learning/",
#     "https://machinelearningmastery.com/what-is-machine-learning/",
#     "https://www.ibm.com/topics/cybersecurity",
#     "https://www.cloudflare.com/learning/security/what-is-cyber-security/",
#     "https://www.techtarget.com/searchsecurity/definition/cybersecurity",
#     "https://aws.amazon.com/what-is-cloud-computing/",
#     "https://azure.microsoft.com/en-us/resources/cloud-computing-dictionary/what-is-cloud-computing",
#     "https://cloud.google.com/learn/what-is-cloud-computing",
#     "https://www.ibm.com/topics/data-science",
#     "https://www.geeksforgeeks.org/data-science/",
#     "https://towardsdatascience.com/what-is-data-science-3d0cdbd0e7e3",
#     "https://builtin.com/robotics",
#     "https://www.techtarget.com/whatis/definition/robotics",
#     "https://aws.amazon.com/what-is/quantum-computing/",
#     "https://www.ibm.com/quantum/learn/what-is-quantum-computing",
#     "https://www.geeksforgeeks.org/quantum-computing/",
#     "https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/HTML_basics",
#     "https://www.freecodecamp.org/news/what-is-programming/",
#     "https://www.geeksforgeeks.org/introduction-to-algorithms/",
#     "https://www.ibm.com/think/topics/blockchain",
#     "https://www.cloudflare.com/learning/network-layer/what-is-iot/",
#     "https://www.oracle.com/artificial-intelligence/what-is-ai/"
# ]
#   crawl_and_analyze(seed_urls, top_n=10)





# import hashlib
# import requests
# from bs4 import BeautifulSoup
# from collections import Counter
# import re
# import os
# from langdetect import detect
# from urllib.parse import urljoin

# # Initialize a queue (set) to keep track of visited URLs
# queue = set()

# def hash_url(url):
#     """Hash the URL using SHA-256."""
#     return hashlib.sha256(url.encode()).hexdigest()

# def fetch_page_content(url):
#     """Fetch the content of a webpage."""
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for HTTP errors
#         return response.text
#     except requests.RequestException as e:
#         print(f"Error fetching {url}: {e}")
#         return None

# def extract_text(content):
#     """Extract the text content from a webpage."""
#     soup = BeautifulSoup(content, "html.parser")
#     return soup.get_text(separator="\n")

# def clean_and_tokenize(text):
#     """Clean text and tokenize into words."""
#     words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())  # Keep words with at least 3 characters
#     return words

# def filter_technology_words(words):
#     """Filter words based on technology-related keywords."""
#     tech_keywords = {
#         'cybersecurity', 'network', 'encryption', 'data', 'technology', 'science', 'cloud',
#         'software', 'hardware', 'ai', 'machine', 'learning', 'robotics', 'automation',
#         'algorithm', 'quantum', 'computing', 'database', 'programming', 'development',
#         'engineering', 'internet', 'digital', 'blockchain', 'virtual', 'reality', 'iot',
#         'innovation', 'biotech', 'nanotechnology', 'genomics'
#     }
#     return [word for word in words if word in tech_keywords]

# def extract_hyperlinks(url, content):
#     """Extract all hyperlinks from a webpage."""
#     soup = BeautifulSoup(content, "html.parser")
#     hyperlinks = set()
#     for link in soup.find_all("a", href=True):
#         href = link.get("href")
#         full_url = urljoin(url, href)
#         if full_url not in queue:  # Only add links that are not already visited
#             hyperlinks.add(full_url)
#     return hyperlinks

# def save_content_to_file(url, content, directory="webpages"):
#     """Save the webpage content to a text file."""
#     if not os.path.exists(directory):
#         os.makedirs(directory)
#     filename = hash_url(url) + ".txt"
#     file_path = os.path.join(directory, filename)
#     with open(file_path, "w", encoding="utf-8") as file:
#         file.write(content)

# def crawl(urls, top_n=10):
#     """Crawl each URL, fetch content, and extract hyperlinks."""
#     to_crawl = set(urls)  # URLs to crawl initially
#     while to_crawl:
#         url = to_crawl.pop()
#         hashed_url = hash_url(url)

#         if hashed_url in queue:
#             continue

#         print(f"Crawling: {url}")
#         queue.add(hashed_url)

#         content = fetch_page_content(url)
#         if not content:
#             continue

#         text = extract_text(content)

#         # Detect language and filter English-only pages
#         try:
#             if detect(text) != 'en':
#                 print(f"Skipping non-English page: {url}")
#                 continue
#         except Exception as e:
#             print(f"Language detection failed for {url}: {e}")
#             continue

#         # Save the page content
#         save_content_to_file(url, text)

#         # Tokenize and rank technology-related words
#         words = clean_and_tokenize(text)
#         tech_words = filter_technology_words(words)
#         word_counts = Counter(tech_words)

#         print(f"Top {top_n} technology-related words from {url}:")
#         for word, count in word_counts.most_common(top_n):
#             print(f"{word}: {count}")

#         # Extract and process hyperlinks
#         hyperlinks = extract_hyperlinks(url, content)
#         filtered_links = filter_science_technology_links(hyperlinks)
#         print(f"Found {len(filtered_links)} science/technology-related hyperlinks on {url}.")

#         # Add filtered links to the crawl queue
#         to_crawl.update(filtered_links)

# def filter_science_technology_links(links):
#     """Filter hyperlinks containing science/technology-related keywords."""
#     science_technology_keywords = [
#         'science', 'technology', 'cybersecurity', 'data', 'engineering', 'computing',
#         'robotics', 'ai', 'machine-learning', 'blockchain', 'iot', 'innovation',
#         'biotech', 'quantum', 'automation', 'digital', 'genomics', 'nanotechnology'
#     ]
#     filtered_links = []
#     for link in links:
#         for keyword in science_technology_keywords:
#             if keyword in link.lower():
#                 filtered_links.append(link)
#                 break
#     return filtered_links

# if __name__ == "__main__":
#     # Example seed URLs
#     seed_urls = [
#         "https://www.cisco.com/site/us/en/learn/topics/security/what-is-cybersecurity.html"
#     ]

#     # Start the crawling process
#     crawl(seed_urls)

import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import hashlib
from urllib.parse import urljoin
import nltk
from nltk.corpus import stopwords
import string
from collections import Counter

# Ensure NLTK resources are available
nltk.download('punkt')
nltk.download('stopwords')

# Hash a URL using SHA-256 for unique identification
def hash_url(url):
    return hashlib.sha256(url.encode()).hexdigest()

# Fetch content from a URL
def fetch_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Extract text content from the webpage
def extract_text(content):
    soup = BeautifulSoup(content, "html.parser")
    return ' '.join(p.get_text() for p in soup.find_all('p'))

# Preprocess text by removing punctuation, numbers, and stopwords
def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ''.join([char for char in text if not char.isdigit()])

    tokens = nltk.word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    return ' '.join(tokens)

# Calculate TF-IDF values for the given text
def calculate_tfidf(text):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray().flatten()

    tfidf_dict = dict(zip(feature_names, tfidf_scores))
    return tfidf_dict

# Sort TF-IDF results in descending order
def sort_tfidf(tfidf_dict):
    sorted_tfidf = sorted(tfidf_dict.items(), key=lambda item: item[1], reverse=True)
    return sorted_tfidf

# Get top N keywords based on TF-IDF scores
def get_top_keywords(sorted_tfidf, top_n=10):
    return sorted_tfidf[:top_n]

# Extract hyperlinks from a webpage
def extract_hyperlinks(url, content):
    soup = BeautifulSoup(content, "html.parser")
    hyperlinks = set()
    for link in soup.find_all("a", href=True):
        full_url = urljoin(url, link.get("href"))
        hyperlinks.add(full_url)
    return hyperlinks

# Main crawling function
def crawl_and_analyze(urls, top_n=10):
    queue = set(urls)
    visited = set()

    while queue:
        url = queue.pop()
        if url in visited:
            continue

        print(f"Crawling: {url}")
        visited.add(url)

        content = fetch_page_content(url)
        if not content:
            continue

        text = extract_text(content)
        preprocessed_text = preprocess_text(text)

        tfidf_dict = calculate_tfidf(preprocessed_text)
        sorted_tfidf = sort_tfidf(tfidf_dict)
        top_keywords = get_top_keywords(sorted_tfidf, top_n=top_n)

        print(f"Top {top_n} keywords from {url}:")
        for keyword, score in top_keywords:
            print(f"{keyword}: {score:.4f}")

        hyperlinks = extract_hyperlinks(url, content)
        queue.update(hyperlinks - visited)

# Example usage
if __name__ == "__main__":
    seed_urls = [
    "https://www.ibm.com/think/topics/artificial-intelligence",
    "https://cloud.google.com/learn/what-is-artificial-intelligence",
    "https://www.geeksforgeeks.org/what-is-ai/",
    "https://www.geeksforgeeks.org/machine-learning/",
    "https://machinelearningmastery.com/what-is-machine-learning/",
    "https://www.ibm.com/topics/cybersecurity",
    "https://www.cloudflare.com/learning/security/what-is-cyber-security/",
    "https://www.techtarget.com/searchsecurity/definition/cybersecurity",
    "https://aws.amazon.com/what-is-cloud-computing/",
    "https://azure.microsoft.com/en-us/resources/cloud-computing-dictionary/what-is-cloud-computing",
    "https://cloud.google.com/learn/what-is-cloud-computing",
    "https://www.ibm.com/topics/data-science",
    "https://www.geeksforgeeks.org/data-science/",
    "https://towardsdatascience.com/what-is-data-science-3d0cdbd0e7e3",
    "https://builtin.com/robotics",
    "https://www.techtarget.com/whatis/definition/robotics",
    "https://aws.amazon.com/what-is/quantum-computing/",
    "https://www.ibm.com/quantum/learn/what-is-quantum-computing",
    "https://www.geeksforgeeks.org/quantum-computing/",
    "https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/HTML_basics",
    "https://www.freecodecamp.org/news/what-is-programming/",
    "https://www.geeksforgeeks.org/introduction-to-algorithms/",
    "https://www.ibm.com/think/topics/blockchain",
    "https://www.cloudflare.com/learning/network-layer/what-is-iot/",
    "https://www.oracle.com/artificial-intelligence/what-is-ai/"
]
    crawl_and_analyze(seed_urls, top_n=10)