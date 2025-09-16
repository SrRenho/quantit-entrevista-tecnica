import chromadb
from embedding import get_embedded_wikipedia_page
from llm import process_valid_query
from commands import print_instructions, is_quitting, is_changing_subject


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