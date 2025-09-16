import re
from wikipedia import prompt_wikipedia_link_or_title, get_sections
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


def sanitize_collection_name(name):
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    return re.sub(r"^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$", "", name)  # remove invalid start/end

def get_embedded_wikipedia_page(chroma_client):
    title, page = prompt_wikipedia_link_or_title()
    sections = get_sections(page)
    sections_texts = [text for _, text in sections]
    print("Embedding Wikipedia page...")
    collection = chroma_client.get_or_create_collection(
        name=sanitize_collection_name(title),
        embedding_function=SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    )
    collection.add(documents=sections_texts, ids=[str(i) for i in range(len(sections_texts))])
    print("Embedding ready")
    return collection