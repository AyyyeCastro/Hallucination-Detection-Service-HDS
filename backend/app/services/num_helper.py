import re

YEAR_PATTERN = r"\b(1[0-9]{3}|20[0-9]{2})\b"
NUMBER_PATTERN = r"\b\d+(?:\.\d+)?\b"
MILLION_PATTERN = r"\b\d+(?:\.\d+)?\s+million\b"


def get_years(text: str) -> set[str]:
    return set(re.findall(YEAR_PATTERN, text))


def get_million_phrases(text: str) -> set[str]:
    return set(re.findall(MILLION_PATTERN, text.lower()))


def get_nums(text: str) -> set[str]:
    return set(re.findall(NUMBER_PATTERN, text))


def _million_base_numbers(million_phrases: set[str]) -> set[str]:
    values = set()
    for phrase in million_phrases:
        match = re.search(NUMBER_PATTERN, phrase)
        if match:
            values.add(match.group(0))
    return values


def compare_num_evidence(claim: str, evidence: str) -> dict:
    claim_years = get_years(claim)
    evidence_years = get_years(evidence)

    claim_millions = get_million_phrases(claim)
    evidence_millions = get_million_phrases(evidence)

    claim_numbers = get_nums(claim)
    evidence_numbers = get_nums(evidence)

    # Remove overlap so years and million values do not get counted twice.
    claim_numbers = claim_numbers - claim_years - _million_base_numbers(claim_millions)
    evidence_numbers = evidence_numbers - evidence_years - _million_base_numbers(evidence_millions)

    year_match = bool(claim_years and claim_years & evidence_years)
    million_match = bool(claim_millions and claim_millions & evidence_millions)
    number_match = bool(claim_numbers and claim_numbers & evidence_numbers)

    return {
        "year_match": year_match,
        "million_match": million_match,
        "number_match": number_match,
        "claim_years": sorted(claim_years),
        "evidence_years": sorted(evidence_years),
        "claim_millions": sorted(claim_millions),
        "evidence_millions": sorted(evidence_millions),
        "claim_numbers": sorted(claim_numbers),
        "evidence_numbers": sorted(evidence_numbers),
    }
