
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

def get_relevant_links(url, keyword_filters=None):
    """
    Extracts all hyperlinks from the given webpage and categorizes them based on relevant keywords.
    
    Parameters:
    - url (str): The webpage URL to scrape.
    - keyword_filters (dict): Dictionary where keys are categories (e.g., AI, ML) and values are lists of relevant keywords.

    Returns:
    - dict: Categorized links {category: [links]}.
    """
    try:
        # Fetch the page content
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract and clean links
        links = set()
        for a in soup.find_all('a', href=True):
            full_link = urljoin(url, a['href'])  # Convert relative URLs to absolute
            links.add(full_link)

        # Categorize links
        categorized_links = {category: [] for category in keyword_filters}

        for link in links:
            for category, keywords in keyword_filters.items():
                if any(keyword in link.lower() for keyword in keywords):
                    categorized_links[category].append(link)
                    break  # Assign to first matching category

        return categorized_links

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return {}

# Define categories and keywords
keyword_filters = {
    "Artificial Intelligence": ["artificial-intelligence", "ai"],
    "Machine Learning": ["machine-learning", "ml"],
    "Robotics": ["robot", "robotics"],
    "Data Science": ["data-science"],
    "Computer Vision": ["computer-vision", "image-recognition"],
    "Quantum Computing": ["quantum-computing"],
    "IoT": ["iot", "internet-things"],
}

# Example usage
url = "https://www.ibm.com/think/topics/artificial-intelligence"
categorized_links = get_relevant_links(url, keyword_filters)

# Print categorized links
for category, links in categorized_links.items():
    print(f"\n🔹 {category} ({len(links)} links):")
    for link in links:
        print(f"  - {link}")
