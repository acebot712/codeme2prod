# advanced_prompt_generator.py

import re
import requests
from bs4 import BeautifulSoup
import os

if os.name == 'posix':  # POSIX is the standard operating system interface usually associated with Unix, Linux.
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    
import chromadb

def extract_links_from_prompt(prompt: str) -> list:
    """
    Extracts and returns all URLs from the provided text.

    :param prompt: The text containing URLs.
    :return: List of extracted URLs.
    """
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    links = url_pattern.findall(prompt)
    return [link.rstrip('.,;!?') for link in links]

def remove_links_from_text(text: str) -> str:
    """
    Removes all URLs from the provided text.

    :param text: The text from which URLs need to be removed.
    :return: Text without URLs.
    """
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.sub('', text)

def fetch_main_text_content(url: str) -> str:
    """
    Fetches and returns the main text content from the provided URL.

    :param url: The URL to fetch the content from.
    :return: Extracted main text content.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Removing script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # Extract text from significant tags
    significant_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'article', 'blockquote', 'div']
    chunks = [element.get_text(strip=True) for tag in significant_tags for element in soup.find_all(tag)]
    return '\n\n'.join(chunk for chunk in chunks if chunk)

def retrieve_documents_from_query(collection, query_text, n_results=1):
    """
    Queries the given ChromaDB collection and returns results.

    :param collection: ChromaDB collection instance.
    :param query_text: Text to query the collection.
    :param n_results: Number of results to fetch.
    :return: Query results.
    """
    return collection.query(query_texts=[query_text], n_results=n_results, include=[ "documents" ])

def add_documents_to_collection(collection, documents, start_id=0):
    """
    Adds documents to the given ChromaDB collection.

    :param collection: ChromaDB collection instance.
    :param documents: List of documents to add.
    :param start_id: Starting ID for the documents.
    :return: Number of documents added.
    """
    ids = [f"doc_{i}" for i in range(start_id, start_id + len(documents))]
    collection.add(documents=documents, ids=ids)
    return len(documents)

def generate_advanced_prompt(prompt_text: str) -> str:
    """
    Generates an advanced prompt by augmenting the given prompt text with information extracted from the mentioned links.

    :param prompt_text: Original prompt text containing URLs.
    :return: Augmented advanced prompt.
    """
    extracted_links = extract_links_from_prompt(prompt_text)
    chroma_client = chromadb.Client()
    all_retrievals = []

    for link in extracted_links:
        collection_name = re.sub(r"[^a-zA-Z0-9]", "_", link)
        collection = chroma_client.create_collection(name=collection_name)

        main_text = fetch_main_text_content(link)
        paragraphs = [p.strip() for p in main_text.split('\n\n') if p.strip()]
        add_documents_to_collection(collection, paragraphs)

        query_text = remove_links_from_text(prompt_text)
        retrievals = retrieve_documents_from_query(collection, query_text=query_text, n_results=1)
        all_retrievals.append(retrievals['documents'][0])
        chroma_client.delete_collection(name=collection_name)

    advanced_prompt = prompt_text
    for idx, retrieval in enumerate(all_retrievals):
        retrieval_text = '\n'.join(retrieval)
        advanced_prompt = f"{prompt_text}\nRelevant extracted content from the links mentioned above for extra context:\nLink {idx + 1}: {extracted_links[idx]}\n{retrieval_text}\n------\n"

    return advanced_prompt

if __name__ == '__main__':
    prompt = "Founded in? Look at https://en.wikipedia.org/wiki/Riot_Games"
    print(generate_advanced_prompt(prompt))
    