from app.services.model_helper import spacy

nlp = spacy.load("en_core_web_sm")

PERSONAL_PRONOUNS = (
    "he", "she", "it", "they", 
    "him", "her", "them",
    "we", "us"
)
POSSESSIVE_PRONOUNS = (
    "his", "her", "hers", "its", "their", "theirs",
)
# DEMONSTRATIVE_PRONOUNS = (
#     "this", "that", "these", "those"
# )
RELATIVE_PRONOUNS = (
    "who", "whom", "whose", "which"
)


ALL_CONTEXT_PRONOUNS = (
    PERSONAL_PRONOUNS + 
    POSSESSIVE_PRONOUNS + 
    # DEMONSTRATIVE_PRONOUNS + 
    RELATIVE_PRONOUNS 
)

def get_subject(claim: str) -> str | None:
    doc = nlp(claim)

    for token in doc:
        if token.dep_ in {"nsubj", "nsubjpass"}:
            for ent in doc.ents:
                if token.i >= ent.start and token.i < ent.end and ent.label_ in {"PERSON", "ORG", "GPE"}:
                    return ent.text

            if token.pos_ in {"PROPN", "NOUN"}:
                return token.text

    for ent in doc.ents:
        if ent.label_ in {"PERSON", "ORG", "GPE"}:
            return ent.text

    return None


def claim_context(claims: list[str]) -> list[dict]:
    context = []
    last_subject = None

    for claim in claims:
        doc = nlp(claim)
        tokens = [token.text for token in doc if not token.is_space]

        subject = get_subject(claim)
        context_based_claim = claim

        if tokens:
            first_token = tokens[0].lower()

            if first_token in PERSONAL_PRONOUNS and last_subject:
                context_based_claim = f"{last_subject} {' '.join(tokens[1:])}"
            elif first_token in POSSESSIVE_PRONOUNS and last_subject:
                context_based_claim = f"{last_subject}'s {' '.join(tokens[1:])}"
            elif first_token in ALL_CONTEXT_PRONOUNS and last_subject:
                context_based_claim = f"{last_subject} {' '.join(tokens[1:])}"

        if subject:
            last_subject = subject

        context.append({
            "original_claim": claim,
            "context_based_claim": context_based_claim
        })

    return context