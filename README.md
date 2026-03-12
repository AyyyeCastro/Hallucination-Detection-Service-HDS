# Hallucination-Detection-Service (HDS)
Analyzes LLM-generated text by extracting factual claims, retrieving supporting evidence from Wikipedia via the MediaWiki API, and scoring semantic alignment between claims and evidence chunks using vector similarity.

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
