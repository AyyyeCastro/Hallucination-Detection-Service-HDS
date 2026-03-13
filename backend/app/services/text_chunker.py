from app.services.model_helper import spacy

nlp = spacy.load("en_core_web_sm")

def text_chunker(text: str, window_size: int = 2, min_words: int = 6) -> list[str]:
    if not text:
        return []

    doc = nlp(text)

    sentences = []
    for sent in doc.sents:
        segmented = sent.text.strip()

        if not segmented:
            continue

        if len(segmented.split()) < min_words:
            continue

        sentences.append(segmented)

    if not sentences:
        return []

    chunks = []
    seen = set()
    

    for i in range(len(sentences)):
        chunk_sentences = sentences[i:i + window_size]

        if not chunk_sentences:
            continue

        chunk = " ".join(chunk_sentences).strip()
        
        if len(chunk.split()) > 80:
            continue

        if chunk and chunk not in seen:
            chunks.append(chunk)
            seen.add(chunk)

    return chunks