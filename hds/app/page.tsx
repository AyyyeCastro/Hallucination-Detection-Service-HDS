"use client";

import { useState } from "react";
import { analyzeText } from "../lib/api";

type ClaimResult = {
  claim: string;
  context_based_claim: string;
  search_query?: string | null;
  subject_search_query?: string | null;
  retrieval_status: string;
  grounding_status: string;
  retrieval_strategy: string;
  contradiction_reason?: string | null;
  score: number;
  semantic_score: number;
  verification: string;
  evidence: string[];
  page_title: string | null;
  matched_numbers: string[];
  mismatched_numbers: string[];
};

type SummaryResult = {
  claims_analyzed: number;
  overall_score: number;
  overall_verification: string;
};

type AnalyzeResponse = {
  claims: ClaimResult[];
  summary: SummaryResult;
};

function getVerificationStyles(label: string) {
  switch (label) {
    case "Verified":
      return "bg-emerald-100 text-emerald-700 border border-emerald-200";
    case "Probable":
      return "bg-blue-100 text-blue-700 border border-blue-200";
    case "Questionable":
      return "bg-amber-100 text-amber-700 border border-amber-200";
    case "Unfounded":
      return "bg-rose-100 text-rose-700 border border-rose-200";
    default:
      return "bg-gray-100 text-gray-700 border border-gray-200";
  }
}

function getRetrievalStyles(status: string) {
  switch (status) {
    case "ok":
      return "bg-emerald-100 text-emerald-700 border border-black-200";
    case "low_semantic_match":
      return "bg-red-100 text-red-700 border border-red-200";
    case "weak_title_match":
    case "low_signal_query":
    case "no_search_results":
    case "no_page_extract":
    case "no_evidence_chunks":
      return "bg-rose-100 text-rose-700 border border-rose-200";
    default:
      return "bg-gray-100 text-gray-700 border border-gray-200";
  }
}
export default function Home() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    if (!text.trim()) return;

    try {
      setLoading(true);
      setError("");
      const data = await analyzeText(text);
      setResult(data);
    } catch {
      setError("Unable to analyze the text. Please try again.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#FFFFFF] text-[#7A7766]">
      <div className="mx-auto max-w-6xl px-6 py-12 md:px-10">
        <header className="mb-10">
          <p className="mb-3 text-sm uppercase tracking-[0.18em] text-[#5F6F88]">
            Hallucination Detection Service (ALPHA)
          </p>

          <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-[#5F6F88] md:text-5xl">
            Compare LLM-generated output against the Wikipedia database.
          </h1>

          <p className="mt-4 max-w-2xl text-base leading-7 text-[#7A7766]">
            A full-stack claim verification system that extracts claims from LLM
            output, resolves contextual references, retrieves external evidence
            from Wikipedia, and evaluates support using semantic similarity and
            numeric consistency checks.
          </p>
        </header>

        <section className="grid gap-8 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="rounded-3xl border border-[#E7E2D6] bg-white p-6 shadow-sm">
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-[#5F6F88]">
                Input Text
              </h2>
              <p className="mt-1 text-sm text-[#7A7766]">
                Paste a response from ChatGPT, Gemini, Claude, or another LLM.
              </p>
            </div>

            <textarea
              className="min-h-[320px] w-full rounded-2xl border border-[#DDD7CA] bg-[#FCFBF8] px-4 py-4 text-sm leading-6 text-[#5F6F88] outline-none transition focus:border-[#5F6F88] focus:ring-2 focus:ring-[#5F6F88]/10"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste LLM output here..."
            />

            <div className="mt-5 flex items-center gap-4">
              <button
                onClick={handleAnalyze}
                disabled={loading || !text.trim()}
                className="rounded-2xl bg-[#5F6F88] px-6 py-3 text-sm font-medium text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Analyzing..." : "Analyze"}
              </button>

              <button
                onClick={() => {
                  setText("");
                  setResult(null);
                  setError("");
                }}
                className="rounded-2xl border border-[#DDD7CA] px-5 py-3 text-sm font-medium text-[#7A7766] transition hover:border-[#5F6F88] hover:text-[#5F6F88]"
              >
                Clear
              </button>
            </div>

            {error && (
              <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {error}
              </div>
            )}
          </div>

          <aside className="rounded-3xl border border-[#E7E2D6] bg-[#FCFBF8] p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-[#5F6F88]">
              How it works
            </h2>

            <div className="mt-5 space-y-4 text-sm leading-6 text-[#7A7766]">
              <div>
                <p className="font-medium text-[#5F6F88]">
                  1. LLM Claim Extraction
                </p>
                <p>
                  Utilizes NLP & custom algorithims to break text into fact-like
                  claims for validation.
                </p>
              </div>

              <div>
                <p className="font-medium text-[#5F6F88]">2. Context Resolution</p>
                <p>
                  Resolves pronouns like “it”, "he", or “they” into clearer
                  claims based on contextual subject.
                </p>
              </div>

              <div>
                <p className="font-medium text-[#5F6F88]">3. Evidence Retrieval</p>
                <p>
                  Attempts searches at relevant source pages and retrieves
                  evidence text for claim validation.
                </p>
              </div>

              <div>
                <p className="font-medium text-[#5F6F88]">4. Verification</p>
                <p>
                  Scores semantic support and checks numeric consistency where
                  possible.
                </p>
              </div>
            </div>
          </aside>
        </section>

        {result && (
          <section className="mt-10 space-y-8">
            <div className="rounded-3xl border border-[#E7E2D6] bg-white p-6 shadow-sm">
              <h2 className="text-xl font-semibold text-[#5F6F88]">Summary</h2>

              <div className="mt-5 grid gap-4 sm:grid-cols-3">
                <div className="rounded-2xl border border-[#EEE8DB] bg-[#FCFBF8] p-4">
                  <p className="text-xs uppercase tracking-wide text-[#7A7766]">
                    Claims Analyzed
                  </p>
                  <p className="mt-2 text-2xl font-semibold text-[#5F6F88]">
                    {result.summary.claims_analyzed}
                  </p>
                </div>

                <div className="rounded-2xl border border-[#EEE8DB] bg-[#FCFBF8] p-4">
                  <p className="text-xs uppercase tracking-wide text-[#7A7766]">
                    Overall Score
                  </p>
                  <p className="mt-2 text-2xl font-semibold text-[#5F6F88]">
                    {result.summary.overall_score.toFixed(2)}
                  </p>
                </div>

                <div className="rounded-2xl border border-[#EEE8DB] bg-[#FCFBF8] p-4">
                  <p className="text-xs uppercase tracking-wide text-[#7A7766]">
                    Overall Verification
                  </p>
                  <div className="mt-2">
                    <span
                      className={`inline-flex rounded-full px-3 py-1 text-sm font-medium ${getVerificationStyles(
                        result.summary.overall_verification
                      )}`}
                    >
                      {result.summary.overall_verification}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h2 className="mb-4 text-xl font-semibold text-[#5F6F88]">
                Claim Results
              </h2>

              <div className="space-y-5">
                {result.claims.map((claim, index) => (
                  <article
                    key={`${claim.claim}-${index}`}
                    className="rounded-3xl border border-[#E7E2D6] bg-white p-6 shadow-sm"
                  >
                    <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                      <div className="max-w-3xl">
                        <p className="text-xs uppercase tracking-wide text-[#7A7766]">
                          Claim {index + 1}
                        </p>
                        <h3 className="mt-2 text-lg font-semibold leading-7 text-[#5F6F88]">
                          {claim.claim}
                        </h3>
                      </div>

                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-sm font-medium ${getVerificationStyles(
                          claim.verification
                        )}`}
                      >
                        {claim.verification}
                      </span>

                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-sm font-medium ${getRetrievalStyles(
                          claim.retrieval_status
                        )}`}
                      >
                        Retrieval: {claim.retrieval_status}
                      </span>

                      <span className="rounded-full border border-[#DDD7CA] px-3 py-1 text-sm text-[#7A7766]">
                        Score: {claim.score.toFixed(2)}
                      </span>
                    </div>

                  
                    <div className="mt-5 grid gap-5 lg:grid-cols-2">
                      <div className="rounded-2xl border border-[#EEE8DB] bg-[#F2EDE0] p-4">
                        <p className="text-sm font-medium text-[#5F6F88]">
                          Context-Based Claim
                        </p>
                        <p className="mt-2 text-sm leading-6 text-[#7A7766]">
                          {claim.context_based_claim}
                        </p>
                      </div>
                      <div className="rounded-2xl border border-[#EEE8DB] bg-[#F2EDE0] p-4">
                        <p className="text-sm font-medium text-[#5F6F88]">
                          Source Page
                        </p>
                        <p className="mt-2 text-sm leading-6 text-[#7A7766]">
                          {claim.page_title ?? "No source found"}
                        </p>
                      </div>
                    </div>

                    <div className="mt-5 rounded-2xl border border-[#EEE8DB] bg-[#F2EDE0] p-4">
                      <p className="text-sm font-medium text-[#5F6F88]">
                        Best Evidence
                      </p>
                      <p className="mt-2 text-sm leading-7 text-[#7A7766]">
                        {claim.evidence?.[0] || "No evidence available."}
                      </p>
                    </div>

                    <div className="mt-5 grid gap-5 md:grid-cols-2">
                      <div className="rounded-2xl border border-[#EEE8DB] bg-[#E5DCC2] p-4">
                        <p className="text-sm font-medium text-[#5F6F88]">
                          Matched Numbers
                        </p>
                        <p className="mt-2 text-sm text-[#7A7766]">
                          {claim.matched_numbers.length > 0
                            ? claim.matched_numbers.join(", ")
                            : "None"}
                        </p>
                      </div>

                      <div className="rounded-2xl border border-[#EEE8DB] bg-[#E5DCC2] p-4">
                        <p className="text-sm font-medium text-[#5F6F88]">
                          Mismatched Numbers
                        </p>
                        <p className="mt-2 text-sm text-[#7A7766]">
                          {claim.mismatched_numbers.length > 0
                            ? claim.mismatched_numbers.join(", ")
                            : "None"}
                        </p>
                      </div>
                    </div>
                    <div className="mt-5 grid gap-5 lg:grid-cols-3">
                      <div className="rounded-2xl border border-[#EEE8DB] bg-[#D9D5C9] p-4">
                        <p className="text-sm font-medium text-[#5F6F88]">Retrieval Query</p>
                        <p className="mt-2 text-sm leading-6 text-[#7A7766]">
                          {claim.search_query ?? "No query generated"}
                        </p>
                      </div>

                      <div className="rounded-2xl border border-[#EEE8DB] bg-[#D9D5C9] p-4">
                        <p className="text-sm font-medium text-[#5F6F88]">Subject Query</p>
                        <p className="mt-2 text-sm leading-6 text-[#7A7766]">
                          {claim.subject_search_query ?? "No subject query"}
                        </p>
                      </div>

                      <div className="rounded-2xl border border-[#EEE8DB] bg-[#D9D5C9] p-4">
                        <p className="text-sm font-medium text-[#5F6F88]">Retrieval Strategy</p>
                        <p className="mt-2 text-sm leading-6 text-[#7A7766]">
                          {claim.retrieval_strategy}
                        </p>
                      </div>
                    </div>

                    <div className="mt-5">
                      <p className="text-sm text-[#7A7766]">
                        Semantic score:{" "}
                        <span className="font-medium text-[#5F6F88]">
                          {claim.semantic_score.toFixed(2)}
                        </span>
                      </p>
                    </div>
                  </article>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-[#E7E2D6] bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-[#5F6F88]">
                  Raw JSON Output
                </h2>
                <span className="text-xs uppercase tracking-wide text-[#7A7766]">
                  Debug View
                </span>
              </div>

              <div className="overflow-x-auto rounded-2xl border border-[#E7E2D6] bg-[#D9D5C9]">
                <pre className="p-5 text-xs leading-6 text-[#5F6F88] whitespace-pre-wrap break-words">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}