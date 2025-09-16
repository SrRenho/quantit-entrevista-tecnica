import os
from dotenv import load_dotenv
from utils import truncate
from openai import OpenAI

load_dotenv()

API_KEY = os.environ.get("API_KEY")
client = OpenAI(api_key=API_KEY)


def format_prompt(question, context):
    context = context if context.strip() != "" else "There's no information provided"
    return  "Information provided: "+context+"\nQuestion: " + question

def process_valid_query(user_input, collection):
    results = collection.query(query_texts=[user_input], n_results=1)
    retrieved_chunk = results['documents'][0][0]

    prompt = format_prompt(user_input, retrieved_chunk)

    # El chatbot no se va a acordar de los mensajes pasados
    # Para solucionarlo, podría simplemente concatenarle los mensajes anteriores, pero como cada mensaje tiene el retrieved_chunk, la context window se llenaría rápido
    # Eso se podría arreglar concatenando los mensajes y respuestas anteriores sin el retrieved_chunk,
    # y/o haciendo que el bot solo recuerde los N mensajes anteriores y se vaya olvidando los viejos,
    # pero entiendo que la idea era no sobrepensar la solución y dejarlo simple
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "You are a concise conversational chatbot. Answer using ONLY the information provided. If the answer is not there, say you don't know."},
            {"role": "user", "content": prompt}
        ]
    )

    print_response(response, retrieved_chunk)

def print_response(response, retrieved_chunk):
    print("\nResponse:", response.choices[0].message.content)
    print("\nSource:", truncate(retrieved_chunk))