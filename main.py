import os
import re
from dotenv import load_dotenv
import wikipediaapi
from openai import OpenAI
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

load_dotenv()

API_KEY = os.environ.get("API_KEY")
client = OpenAI(api_key=API_KEY)

wiki = wikipediaapi.Wikipedia(user_agent="Entrevista Técnica", language="en")

def prompt_wikipedia_link_or_title():
    while True:
        user_input = input("Enter a Wikipedia link or page title: ").strip()
        if not user_input:
            print("Input cannot be empty.")
            continue

        if "wikipedia.org" in user_input:
            title = user_input.split("/")[-1].replace("_", " ")
        else:
            title = user_input

        page = wiki.page(title)
        if not page.exists():
            print("Page does not exist. Please enter a valid Wikipedia link or title.")
            continue

        log_found_page(title, page)
        return title, page

def get_sections(page):
    sections = []
    def recurse_sections(s, parent_title=""):
        for sec in s.sections:
            full_title = f"{parent_title} > {sec.title}" if parent_title else sec.title
            sections.append((full_title, sec.text))
            recurse_sections(sec, full_title)
    recurse_sections(page)
    return sections

def format_prompt(question, context):
    context = context if context.strip() != "" else "There's no information provided"
    return  "Information provided: "+context+"\nQuestion: " + question

def log_found_page(title, page):
    print("Found the page",title + ":")
    print(truncate(page.text))

quitting_commands = ['quit', 'q', 'exit']
changing_subject_commands = ['change subject', 'change', 'c']

def format_command_options(command_options):
    return ", ".join(f"'{s}'" for s in command_options[:-1]) + f", or '{command_options[-1]}'"

def is_quitting(user_input):
    return user_input in quitting_commands

def is_changing_subject(user_input):
    return user_input in changing_subject_commands


def print_instructions():
    print("To quit write " + format_command_options(quitting_commands))
    print("To change subject write " + format_command_options(changing_subject_commands))

def sanitize_collection_name(name):
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)  # replace invalid chars
    return re.sub(r"^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$", "", name)  # remove invalid start/end


def get_embedded_wikipedia_page(chroma_client):
    title, page = prompt_wikipedia_link_or_title()
    sections = get_sections(page)
    sections_texts = [text for _, text in sections]
    print("Embedding wikipedia page...")
    collection = chroma_client.get_or_create_collection(
        name=sanitize_collection_name(title),
        embedding_function=SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    )
    collection.add(documents=sections_texts, ids=[str(i) for i in range(len(sections_texts))])
    print("Embedding ready")
    return collection


def process_valid_query(user_input, collection):
    results = collection.query(query_texts=[user_input], n_results=1)
    retrieved_chunk = results['documents'][0][0]
    prompt = format_prompt(user_input, retrieved_chunk)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "You are a concise conversational chatbot. Answer using ONLY the information provided. If you the answer is not there, say you don't know."},
            {"role": "user", "content": prompt}
        ]
    )
    print("\nResponse:", response.choices[0].message.content)
    print("\nSource:", truncate(retrieved_chunk))

def truncate(text, char_limit=200):
    return text if len(text) < char_limit else text[:char_limit] + " (...)"

if __name__ == '__main__':
    print_instructions()

    chroma_client = chromadb.Client()
    collection = get_embedded_wikipedia_page(chroma_client)

    while True:
        user_input = input("\nAsk something: ")

        if is_quitting(user_input):
            break

        elif is_changing_subject(user_input):
            collection = get_embedded_wikipedia_page(chroma_client)
            continue

        process_valid_query(user_input, collection)