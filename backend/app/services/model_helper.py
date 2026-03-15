from functools import lru_cache
import spacy

@lru_cache(maxsize=1)
def get_nlp():
    return spacy.load("en_core_web_sm")

def nlp(text: str):
    return get_nlp()(text)