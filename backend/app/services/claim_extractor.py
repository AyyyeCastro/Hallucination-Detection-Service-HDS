from app.services.model_helper import spacy
from app.services.clause_helper import split_extensive_claims

nlp = spacy.load("en_core_web_sm")

EPISTEMIC_PREFIXES = (
    "it seems", "it appears", "i suspect", "in my opinion",
    "it is possible", "i guess", "i think", "i wonder",
    "supposedly", "allegedly", "arguably", "conceivably",
    "i believe", "i assume", "i imagine", "i feel",
    "to me", "from my perspective", "rumor has it",
    "some say", "it could be", "it might be", "maybe",
    "perhaps", "chances are", "i bet", "i have a feeling",
    "it's likely", "it is unlikely", "hopefully", "ideally",
)

DIRECTIVE_PREFIXES = (
    "give me", "show me", "provide", "search for",
    "look up", "explain", "describe", "assist me",
    "would you", "help me with", "tell me", "generate",
    "create", "write", "list", "summarize", "analyze",
    "find", "can you", "could you", "please",
    "i need", "i want", "i would like", "let's",
    "draft", "translate", "compare", "evaluate",
)

INTERROGATIVE_PREFIXES = (
    "what is", "do you know", "is there", "are there",
    "where is", "when was", "how many", "how much",
    "how long", "should i", "is it", "why is",
    "why does", "how do", "how does", "who is",
    "who was", "which", "what are", "what were",
    "could it be", "did you", "have you", "has anyone",
)

HYPOTHETICAL_PREFIXES = (
    "what if", "if we", "assuming", "suppose",
    "imagine if", "in the event that", "let's say",
    "if i were to", "hypothetically",
)

ALL_NON_FACTUAL_PREFIXES = (
    EPISTEMIC_PREFIXES
    + DIRECTIVE_PREFIXES
    + INTERROGATIVE_PREFIXES
    + HYPOTHETICAL_PREFIXES
)

BAD_CLAUSE_STARTERS = {
    "while", "which", "who", "that", "because", "although", "though", "since"
}


def possible_claim(sentence) -> bool:
    text = sentence.text.strip()
    lower_text = text.lower()

    if not text or text.endswith("?"):
        return False

    if len(text.split()) < 6:
        return False

    if lower_text.startswith(ALL_NON_FACTUAL_PREFIXES):
        return False

    first_token = next((t for t in sentence if not t.is_space and not t.is_punct), None)
    if first_token and first_token.text.lower() in BAD_CLAUSE_STARTERS:
        return False

    has_subject = any(token.dep_ in {"nsubj", "nsubjpass"} for token in sentence)
    has_finite_verb = any(
        token.pos_ in {"VERB", "AUX"} and token.dep_ in {"ROOT", "ccomp", "xcomp", "relcl", "advcl"}
        for token in sentence
    )

    if not has_subject:
        return False
    if not has_finite_verb:
        return False

    if lower_text.startswith(("which ", "who ", "that ", "while ", "because ")):
        return False

    return True


def extract_claims(text: str) -> list[str]:
    candidate_claims = split_extensive_claims(text)
    claims = []
    seen = set()

    for candidate in candidate_claims:
        doc = nlp(candidate)
        sentence = doc[:]

        segmented = candidate.strip()
        if not segmented:
            continue

        if possible_claim(sentence) and segmented not in seen:
            claims.append(segmented)
            seen.add(segmented)

    return claims