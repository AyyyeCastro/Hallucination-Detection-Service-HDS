from app.services.model_helper import nlp

CLAUSE_CONNECTORS = {"but"}

BAD_RIGHT_STARTERS = {
    "which",
    "who",
    "that",
    "while",
    "because",
    "although",
    "though",
    "since",
}

def get_subject_text(span) -> str | None:
    for token in span:
        if token.dep_ in {"nsubj", "nsubjpass"}:
            subtree = sorted(list(token.subtree), key=lambda t: t.i)
            return " ".join(tok.text for tok in subtree)
    return None

def has_finite_verb(span) -> bool:
    # Slightly stricter than before: require a verb/aux that looks clause-like
    return any(
        token.pos_ in {"VERB", "AUX"}
        and token.dep_ in {"ROOT", "conj", "ccomp", "xcomp", "advcl", "relcl"}
        for token in span
    )

def has_subject(span) -> bool:
    return any(token.dep_ in {"nsubj", "nsubjpass", "expl"} for token in span)

def clean_clause_text(text: str) -> str:
    text = text.strip(" ,;:-\n\t")
    text = " ".join(text.split())

    if not text:
        return ""

    if not text.endswith((".", "!", "?")):
        text += "."

    return text

def is_bad_split_connector(token) -> bool:
    """
    Reject connectors that are likely inside a noun/list coordination
    rather than between two clauses.
    """
    if token.text.lower() not in CLAUSE_CONNECTORS:
        return True

    head = token.head

    if head.pos_ in {"NOUN", "PROPN", "NUM"}:
        return True

    return False

def looks_like_independent_right_clause(right_span) -> bool:
    """
    Require the right side to look like a real clause, not just a tail fragment.
    """
    if len(right_span.text.split()) < 4:
        return False

    first_real = next((t for t in right_span if not t.is_space and not t.is_punct), None)
    if first_real and first_real.text.lower() in BAD_RIGHT_STARTERS:
        return False

    if not has_finite_verb(right_span):
        return False

    return True


def can_split_on_connector(token, sentence, left_span, right_span) -> bool:
    """
    Allow splitting only when the connector appears to join clause-like spans.
    """
    if is_bad_split_connector(token):
        return False

    if not left_span.text.strip() or not right_span.text.strip():
        return False

    if not has_finite_verb(left_span):
        return False

    if not looks_like_independent_right_clause(right_span):
        return False

    return True


def split_sentence_into_clauses(sentence) -> list[str]:
    tokens = [token for token in sentence if not token.is_space]
    if not tokens:
        return []

    subject_text = get_subject_text(sentence)

    for i, token in enumerate(tokens):
        if token.text.lower() not in CLAUSE_CONNECTORS:
            continue

        left = tokens[:i]
        right = tokens[i + 1:]

        if not left or not right:
            continue

        left_span = sentence.doc[left[0].i : left[-1].i + 1]
        right_span = sentence.doc[right[0].i : right[-1].i + 1]

        if not can_split_on_connector(token, sentence, left_span, right_span):
            continue

        left_text = clean_clause_text(left_span.text)
        right_text = right_span.text.strip()

        # Only inject subject when the right side is already clause-like
        # but missing an explicit subject.
        if right_text and not has_subject(right_span) and subject_text:
            right_text = f"{subject_text} {right_text}"

        right_text = clean_clause_text(right_text)

        clauses = []
        if left_text:
            clauses.append(left_text)
        if right_text:
            clauses.append(right_text)

        return clauses

    cleaned = clean_clause_text(sentence.text)
    return [cleaned] if cleaned else []


def split_extensive_claims(text: str) -> list[str]:
    doc = nlp(text)
    claims = []

    for sentence in doc.sents:
        claims.extend(split_sentence_into_clauses(sentence))

    return claims