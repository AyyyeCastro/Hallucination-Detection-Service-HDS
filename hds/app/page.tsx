"use client";

import { useState } from "react";
import { analyzeText } from "../lib/api";

export default function Home() {

  const [text, setText] = useState("");
  const [result, setResult] = useState<any>(null);

  async function handleAnalyze() {
    const data = await analyzeText(text);
    console.log(data);
    setResult(data);
  }

  return (
    <div className="p-10 max-w-xl mx-auto">

      <h1 className="text-2xl font-bold mb-4">
        Hallucination Detection Service (HDS)
      </h1>

      <textarea
        className="w-full border p-4 mb-4 rounded"
        rows={8}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste LLM output here"
      />

      <button
        onClick={handleAnalyze}
        className="bg-green-700 text-white px-6 py-2 rounded"
      >
        Analyze
      </button>

      {result && (
        <pre className="p-5 mt-10 bg-gray-200 p-4 overflow-auto border rounded">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}

    </div>
  );
}