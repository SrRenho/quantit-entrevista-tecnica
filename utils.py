def truncate(text, char_limit=200):
    return text if len(text) < char_limit else text[:char_limit] + " (...)"
