import wikipediaapi
from utils import truncate

wiki = wikipediaapi.Wikipedia(user_agent="Entrevista Técnica Quantit", language="en")

def is_a_wikipedia_link(text):
    return "wikipedia.org" in text

def get_title_from_wikipedia_link(wikipedia_link):
    return wikipedia_link.split("/")[-1].replace("_", " ")

def prompt_wikipedia_link_or_title():
    while True:
        user_input = input("Enter a Wikipedia link or page title: ").strip()
        if not user_input:
            print("Input cannot be empty.")
            continue

        title = get_title_from_wikipedia_link(user_input) if is_a_wikipedia_link(user_input) else user_input
        page = wiki.page(title)

        if not page.exists():
            print("Page does not exist. Please enter a valid Wikipedia link or title.")
            continue

        log_found_page(title, page)
        return title, page

def get_sections(page):
    sections = []

    def recurse_sections(s, parent_title=""):
        full_title = f"{parent_title} > {s.title}" if parent_title else s.title
        sections.append((full_title, s.text))

        for sec in s.sections:
            recurse_sections(sec, full_title)

    recurse_sections(page)

    return sections

def log_found_page(title, page):
    print("Found the page",title + ":")
    print(truncate(page.text))
