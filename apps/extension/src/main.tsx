import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import "./index.css";

const App = () => {
  const [result, setResult] = useState("Click to score");
  const [loading, setLoading] = useState(false);

  const score = () => {
    setLoading(true);
    setResult("Analyzing...");
    chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
      chrome.runtime.sendMessage({ action: "score", url: tab.url }, (res) => {
        if (res.data) {
          const d = res.data;
          let out = `Score: ${d.score} (${d.label})\n\n`;
          d.evidence.forEach((e: any) => {
            out += `${e.title}\n  ${e.summary}\n\n`;
          });
          setResult(out.trim());
        } else {
          setResult("Error: " + (res.error || "Unknown"));
        }
        setLoading(false);
      });
    });
  };

  return (
    <div className="p-4 w-96 font-sans">
      <h1 className="text-2xl font-bold text-blue-600 text-center mb-3">
        TrustLens AI
      </h1>
      <button
        onClick={score}
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Score This Page"}
      </button>
      <pre className="mt-4 text-xs bg-gray-100 p-3 rounded max-h-96 overflow-y-auto whitespace-pre-wrap">
        {result}
      </pre>
    </div>
  );
};

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
