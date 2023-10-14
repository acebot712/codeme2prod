import re
import requests
from bs4 import BeautifulSoup
import chromadb

def extract_links_from_prompt(prompt: str):
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    links = url_pattern.findall(prompt)
    cleaned_links = [link.rstrip('.,;!?') for link in links]
    return cleaned_links

def remove_links_from_text(text: str):
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.sub('', text)

def fetch_main_text_content(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Removing script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # Extract text from significant tags
    significant_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'article', 'blockquote', 'div']
    chunks = []
    for tag in significant_tags:
        chunks.extend([element.get_text(strip=True) for element in soup.find_all(tag)])

    return '\n\n'.join(chunk for chunk in chunks if chunk)

def retrieve_documents_from_query(collection, query_text, n_results=1):
    results = collection.query(query_texts=[query_text], n_results=n_results, include=[ "documents" ])
    return results

def add_documents_to_collection(collection, documents, start_id=0):
    ids = [f"doc_{i}" for i in range(start_id, start_id + len(documents))]
    collection.add(documents=documents, ids=ids)
    return len(documents)  # Return the number of documents added

def generate_advanced_prompt(prompt_text: str) -> str:
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

    advanced_prompt = ""
    for idx, retrieval in enumerate(all_retrievals):
        retrieval_text = '\n'.join(retrieval)
        advanced_prompt += f"{prompt_text}\nRelevant extracted content from the links mentioned above for extra context:\nLink {idx + 1}: {extracted_links[idx]}\n{retrieval_text}\n------\n"

    return advanced_prompt

if __name__ == '__main__':
    prompt = """
    It was founded in September 2006 by Brandon Beck and Marc Merrill to develop League of Legends and went on to develop several spin-off https://en.wikipedia.org/wiki/Riot_Games
    """
    print(generate_advanced_prompt(prompt))
    