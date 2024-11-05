import langid

def detect_language(text: str) -> tuple:
    return langid.classify(text)[0]
