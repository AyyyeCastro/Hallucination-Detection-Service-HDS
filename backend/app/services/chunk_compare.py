from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def find_best_match(claim: str, chunks: list[str]) -> dict:
    if not chunks:
        return {
            "best_chunk": None,
            "score": 0.0
        }

    claim_embedding = model.encode(claim, convert_to_tensor=True)
    chunk_embeddings = model.encode(chunks, convert_to_tensor=True)

    similarities = util.cos_sim(claim_embedding, chunk_embeddings)[0]
    best_index = similarities.argmax().item()
    best_score = float(similarities[best_index])

    return {
        "best_chunk": chunks[best_index],
        "score": best_score
    }