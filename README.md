# Hallucination-Detection-Service (HDS)
Analyzes LLM-generated text by extracting factual claims, retrieving supporting evidence from Wikipedia via the MediaWiki API, and scoring semantic alignment between claims and evidence chunks using vector similarity.

### Table of Contents

- [V2.5 (Beta)](#v25-beta)
- [V2: Beta Phase](#v2-beta-phase)
- [V1: Alpha Phase](#v1-alpha-phase)
- [Notes / Limitations](#notes--limitations)

---

## V2.5 (Beta)

Further optimized evidence retrieval, claim extraction, and per-claim contextual reference resolution for LLM output. In V2, false positives were a persistent issue. V2.5 addresses this with stricter claim extraction, less aggressive clause splitting, better LLM-output cleanup, safer context-aware pronoun resolution, subject-first retrieval with claim fallback, richer retrieval diagnostics, contradiction-aware verification, improved numeric comparison, expanded API debug output, and more conservative overall summary logic.

Users can now better understand how evidence was retrieved through explicit retrieval statuses, retrieval strategy indicators, and visible keyword queries used during evidence lookup.

Detailed changes are below.

### Input cleanup and preprocessing

- Added `clean_LLM_text()` preprocessing before analysis so raw model output is normalized before claim extraction.
- Normalized curly quotes and punctuation.
- Removed list markers and inline citation artifacts such as:
  - numbered prefixes
  - `+1`
  - `[1]`
- Collapsed whitespace and normalized punctuation spacing.
- Preserved cleaner text before the claim extraction stage.

### Claim extraction improvements

- Tightened claim filtering to reduce malformed or dependent fragments.
- Rejected more low-quality fragments such as:
  - relative-clause fragments
  - subordinate fragments
  - question-like statements
  - short incomplete fragments
- Added explicit bad clause starters to reject fragments beginning with words like:
  - `which`
  - `who`
  - `that`
  - `while`
  - `because`
- Required stronger grammatical structure for extracted claims:
  - explicit subject
  - finite verb
  - more sentence-like structure
- Reduced fragment leakage from numbered or stylized LLM outputs.

### Clause splitting improvements

- Made clause splitting much less aggressive.
- Stopped splitting on broad connector sets and restricted splitting primarily to safer cases.
- Avoided splitting inside coordinated noun phrases and list-like structures.
- Added stronger right-clause validation before allowing a split.
- Prevented clause splitting from manufacturing broken claims like:
  - dangling tails
  - noun-list fragments
  - clauses missing a subject/predicate relationship

### End-to-end analysis flow

- Improved the end-to-end analysis flow to:
  - clean input text first
  - extract claims more conservatively
  - resolve context with safer subject replacement
  - verify claims with richer retrieval and contradiction handling
- Separated retrieval quality from verification outcome so failed retrieval is no longer treated the same as unsupported evidence.

### Context and reference resolution

- Reworked context-aware subject replacement to better preserve discourse context.
- Made context replacement safer and less likely to rewrite junk fragments into new junk.
- Reduced aggressive handling of relative pronouns.
- Improved contextual claim building so downstream retrieval has better entity grounding.

### Retrieval strategy improvements

- Added logic to distinguish:
  - subject-grounded retrieval
  - full-claim fallback retrieval
- Made retrieval strategy explicit in output so debugging is easier.
- Added structured retrieval outcome labels instead of treating all weak retrieval as simple unsupported evidence.

### Query building improvements

- Reworked query building to preserve stronger anchors such as:
  - named entities
  - dates
  - quoted phrases
  - major relation terms
- Improved selection of primary subjects for retrieval.
- Added handling to prefer stronger entities over weak generic subjects via weighting logic.
- Reduced low-signal subject grounding.
- Improved deduplication of repeated query terms.
- Improved date handling in generated queries.
- Reduced generic keyword soup and increased anchor quality.

### Subject grounding improvements

- Added stronger detection of whether a claim subject is actually grounded.
- Added subject quality checks to reject weak or generic subject phrases.
- Improved entity preference so longer and more informative entities are favored over ambiguous short ones.
- Added explicit grounding states in output.

### Verification improvements

- Replaced the older score-only verification framing with richer final outcomes.
- Added clearer verification categories:
  - `Supported`
  - `Contradicted`
  - `Insufficient Evidence`
  - `Retrieval Failed`
  - `Malformed Claim`
- Stopped overloading one generic `Unfounded` bucket for all failure modes.
- Separated:
  - retrieval failure
  - contradiction
  - insufficient evidence
  - malformed claims
- Improved semantic-verification behavior so retrieval quality and evidence support are treated as different layers.

### Contradiction handling

- Added a new verification helper layer for contradiction-style checks.
- Added heuristic contradiction handling for cases such as:
  - year mismatch
  - birthplace / death-place mismatch
  - nationality or origin mismatch
  - some attribute/property mismatch cases
- Made contradiction reasoning explicit in the output with `contradiction_reason`.

### Retrieval diagnostics and debuggability

- Added explicit retrieval-state reporting, including support for cases like:
  - low-signal query
  - no search results
  - weak title match
  - missing extract
  - low semantic match
- Filtered out many false-positive weak retrievals that previously looked like successful evidence matching.
- Made the JSON output much more transparent for debugging false positives and false negatives.

### Numeric comparison improvements

- Improved number comparison logic to avoid duplicated numeric signals.
- Prevented values inside “million” phrases from also being counted as generic numbers.
- Deduped numeric result arrays more cleanly.

### API and response schema updates

- Expanded claim result payloads to include richer debug fields:
  - `subject_search_query`
  - `retrieval_status`
  - `grounding_status`
  - `retrieval_strategy`
  - `contradiction_reason`
- Updated result-building logic so claim output better reflects retrieval and verification separately.
- Preserved existing scoring and evidence fields while making result interpretation more transparent across the system.

### Overall summary logic

- Improved summary labeling away from the original overly optimistic score-only approach.
- Changed overall summary behavior to be more conservative.
- Roughly 75% of claims now need to be supported for the overall result to be labeled `Supported`.
- Prevented a single supported claim plus a decent average score from making the whole document look `Supported`.
- Added logic so contradiction and retrieval failure states influence the overall result more appropriately.
- instead of overusing `Supported`, shifted the default overall summary toward: 
  - `Insufficient Evidence`
  - `Contradicted`
  - `Retrieval Failed`



### New verification helper

- Added `verification_helper.py` to support contradiction-aware verification and richer reasoning over retrieved evidence.

---

## Notes / Limitations

This is still a beta release and there are significant inaccuracies.

This project is **not**:
- Google
- a general-purpose search engine (although, it shares similarities!)
- a 100% accurate fact checker

Current limitations still include:
- semantic-similarity overmatching or undermatching
- imperfect Wikipedia API querying and page selection
- retrieval edge cases for obscure, composite, or highly interpretive claims
- heuristic contradiction logic that is useful but not exhaustive

This version is a substantial improvement over V2 in transparency, debugging, and retrieval-aware verification, but it should still be treated as an iterative verification system rather than a final authority on factual accuracy. 

This is a portfolio project meant to demonstrate ability for recruiters, not large-scale or production grade fact checking. Please keep in mind I am only a single person with no budget. :) 

## V2: Beta Phase

V2 expands HDS from a working end-to-end prototype into a more structured claim verification system. This version improves evidence retrieval quality, introduces contextual claim rewriting for pronoun-based claims, adds per-claim verification metadata, and upgrades the frontend into a more polished interface. While the system is still not a perfect fact-checker, V2 produces significant upgrades and more explainable results than the original alpha release.

### What changed in V2

* Refactored the backend into a cleaner service-oriented pipeline so orchestration, result shaping, and summary generation are separated from the route layer.
* Added contextual claim rewriting to resolve pronoun-based claims such as “He” and “His” into stronger, retrieval-ready claim forms.
* Improved factual claim extraction with stronger grammatical filtering while still allowing contextual claims to pass for later resolution.
* Added clause splitting for compound sentences so multiple factual statements inside one sentence can be checked separately (ex. "and", "but", "although", etc..).
* Added a dedicated query builder that transforms raw claims into key words for Wikipedia search queries.
* Added further evidence (text gathered from Wikipedia) cleaning to remove noisy artifacts before chunking and comparison.
* Improved chunking by moving to smaller, sentence-window-based evidence chunks for more focused semantic matching.
* Integrated semantic similarity scoring with better evidence selection for each extracted claim.
* Added numeric and date-aware verification logic to enhance accuracy weight when evidence matches exact years or numbers (weighted more towards years or numerical phrases [ex. 1 million], as raw numbers can trigger false possitives more often).
* Added per-claim metadata including:
  * `context_based_claim`
  * `page_title`
  * `matched_numbers`
  * `mismatched_numbers`
  * `semantic_score`
* Added an overall response summary that aggregates all claim scores into a final verification score and label, for the full LLM output accuracy.
* Significantly improved retrieval relevance during iterative development testing by introducing contextualized claims, query building, improved page-title selection, and evidence cleaning.
* Reworked the frontend into a cleaner modern interface using Next.js and Tailwind CSS.
* Added styled summary cards, claim result cards, loading state, clear action, and verification badges in the UI.

### Current V2 limitations

* Verification is still based primarily on retrieved evidence support, semantic similarity, and numeric/date matching. It is not a full contradiction-aware fact-checking engine. (i.e it is not a search engine... But, it's getting close!)
* Some broad, nuanced, or multi-hop claims may still retrieve weak or incomplete evidence. (ex. "Albert Einstein changed the world" -- is hard to prove as true or false directly)
* Contradiction detection is not yet implemented. Possible in V3!


# V1: Alpha Phase
The core architecture of the system is complete, and working. However, LLM  fact-verification/accuracy needs significant refinement; likely due to chunk processing and comparison. V1 is simply intended to be a working and stable full-stack project. Further refinement coming in the future. Detailed log below.

* Created a separate structure with a Next.js frontend (hds/) and FastAPI backend (backend/) to reflect a real service-oriented architecture.
* Set up the FastAPI backend entry point in app/main.py, including app initialization, router registration, and CORS configuration for communication with the Next.js frontend.
* Defined backend request/response contracts with Pydantic schemas for analysis requests and claim-level verification results.
* Built the /analyze API route to accept raw LLM-generated text, process it through the verification pipeline, and return structured JSON results.
* Implemented an NLP based claim extraction pipeline with spaCy to segment LLM output into sentences and filter for likely factual, verifiable claims.
* Added filtering logic to reject questions, opinion-based phrasing, instructional prompts, very short fragments, and sentences without meaningful grammatical structure.
* Integrated the backend with the Next.js frontend and verified end-to-end communication from the browser UI to the FastAPI /analyze endpoint.
* Added a simple (skeleton) frontend interface in Next.js for pasting model output, submitting it for analysis, and rendering the returned JSON results.
* Integrated the MediaWiki/Wikipedia API as the project’s external knowledge source, enabling automated retrieval of encyclopedia-based evidence for extracted factual claims.
* Implemented a Wikipedia content retrieval service to fetch plain-text article extracts for selected pages.
* Added required HTTP headers, including a custom User-Agent, to comply with Wikimedia API access requirements and resolve request failures.
* Built an evidence retrieval layer that takes a claim, searches Wikipedia, selects a candidate page, fetches its content, and returns that content for downstream verification.
* Wired evidence retrieval directly into /analyze so claim results now include retrieved evidence text rather than placeholder output.
* Implemented a text chunking layer to split retrieved evidence into smaller segments for comparison instead of evaluating entire article extracts as one block.
* Integrated sentence-transformer embeddings to compare each claim against evidence chunks using semantic similarity.
* Built a chunk comparison layer to identify the most relevant supporting evidence chunk for a given claim.
* Created a claim verification layer that combines evidence retrieval, chunking, and embedding-based similarity matching into one reusable service.
* Added an LLM claim scoring mapping system to convert similarity scores (how similar it is to the retrieved facts) into verification states such as has_verification, little_verification, and hallucination. It's then calculated into an overall hallucination_score for the response by aggregating per-claim support scores.
* Verified the full V1 pipeline in the frontend with real example claims, confirming the system now supports claim extraction > retrieval > evidence matching > scoring > UI display.
* Documented the main V1 limitation: verification score currently measures semantic similarity, not exact fact contradiction detection, so accuracy improvements are planned for later iterations.
