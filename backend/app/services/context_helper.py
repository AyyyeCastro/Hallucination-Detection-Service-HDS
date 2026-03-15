from app.services.model_helper import nlp

PERSONAL_PRONOUNS = (
    "he", "she", "it", "they",
    "him", "her", "them",
    "we", "us"
)

POSSESSIVE_PRONOUNS = (
    "his", "her", "hers", "its", "their", "theirs",
)

RELATIVE_PRONOUNS = (
    "who", "whom", "whose", "which"
)

ALL_CONTEXT_PRONOUNS = (
    PERSONAL_PRONOUNS +
    POSSESSIVE_PRONOUNS
)

def get_subject(claim: str) -> str | None:
    doc = nlp(claim)

    # prefer subjects named.
    for token in doc:
        if token.dep_ in {"nsubj", "nsubjpass"}:
            for ent in doc.ents:
                if ent.start <= token.i < ent.end and ent.label_ in {"PERSON", "ORG", "GPE"}:
                    return ent.text

            # expand to the token subtree for slightly better noun phrases extracted.
            if token.pos_ in {"PROPN", "NOUN"}:
                subtree = list(token.subtree)
                subtree = sorted(subtree, key=lambda t: t.i)
                text = " ".join(t.text for t in subtree if not t.is_space)
                return text.strip()

    # Fallback case!
    for ent in doc.ents:
        if ent.label_ in {"PERSON", "ORG", "GPE"}:
            return ent.text

    return None


def has_explicit_subject(doc) -> bool:
    return any(token.dep_ in {"nsubj", "nsubjpass"} for token in doc)


def has_finite_verb(doc) -> bool:
    for token in doc:
        if token.pos_ in {"VERB", "AUX"}:
            if token.dep_ in {"ROOT", "ccomp", "xcomp", "advcl", "relcl"}:
                return True
    return False


def starts_with_rewritable_pronoun(doc) -> tuple[str | None, str | None]:
    for token in doc:
        if token.is_space or token.is_punct:
            continue

        text = token.text.lower()

        if text in PERSONAL_PRONOUNS:
            return "personal", token.text
        if text in POSSESSIVE_PRONOUNS:
            return "possessive", token.text

        # First real token is not a rewritable pronoun.
        return None, None

    return None, None


def is_bad_rewrite_candidate(doc) -> bool:
    """
    Reject obvious fragments or clause types that should not be repaired
    by prefixing the last subject.
    """
    first_real_token = None
    for token in doc:
        if not token.is_space and not token.is_punct:
            first_real_token = token
            break

    if not first_real_token:
        return True

    first = first_real_token.text.lower()

    if first in {
        "which", "who", "whom", "whose",
        "because", "although", "while", "when", "if", "that"
    }:
        return True

    # Very short fragments are typically junk in this stage, so we can probably toss it.
    non_punct_tokens = [t for t in doc if not t.is_space and not t.is_punct]
    if len(non_punct_tokens) < 4:
        return True

    if not has_finite_verb(doc):
        return True

    return False


def can_use_as_context_subject(subject: str | None) -> bool:
    if not subject:
        return False

    subject = subject.strip()
    if not subject:
        return False

    lowered = subject.lower()

    if lowered in ALL_CONTEXT_PRONOUNS or lowered in RELATIVE_PRONOUNS:
        return False

    # single-character subjects aren't useful..
    if len(subject) < 2:
        return False

    return True


def rewrite_claim_with_context(doc, last_subject: str) -> str:
    tokens = [token.text for token in doc if not token.is_space]
    if not tokens:
        return doc.text.strip()

    pronoun_type, _ = starts_with_rewritable_pronoun(doc)
    if pronoun_type is None:
        return doc.text.strip()

    rest = " ".join(tokens[1:]).strip()
    if not rest:
        return doc.text.strip()

    if pronoun_type == "possessive":
        return f"{last_subject}'s {rest}"

    return f"{last_subject} {rest}"


def claim_context(claims: list[str]) -> list[dict]:
    context = []
    last_subject = None

    for claim in claims:
        doc = nlp(claim)
        subject = get_subject(claim)
        context_based_claim = claim.strip()

        pronoun_type, _ = starts_with_rewritable_pronoun(doc)

        should_rewrite = (
            pronoun_type is not None
            and last_subject is not None
            and not is_bad_rewrite_candidate(doc)
            and not has_explicit_subject(doc)
        )

        if should_rewrite:
            rewritten = rewrite_claim_with_context(doc, last_subject)
            # Only accept rewrite if it still parses as clause-like text.
            rewritten_doc = nlp(rewritten)
            if has_finite_verb(rewritten_doc):
                context_based_claim = rewritten

        # Update subject memory only from strong subjects.
        if can_use_as_context_subject(subject):
            last_subject = subject

        context.append({
            "original_claim": claim,
            "context_based_claim": context_based_claim
        })

    return context