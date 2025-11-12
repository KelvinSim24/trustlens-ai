import { useState } from "react";
import axios from "axios";

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const check = async () => {
    if (!url) return;
    setLoading(true);
    try {
      const res = await axios.post(
        "http://localhost:8080/v1/score",
        { url },
        {
          headers: { "Content-Type": "application/json" },
          timeout: 100000,
        }
      );
      setResult(res.data);
    } catch (e: any) {
      if (e.code === "ERR_NETWORK" || e.message.includes("timeout")) {
        alert("Taking longer than usual... Still analyzing. Try again in 10s.");
      } else {
        alert("Error: " + (e.response?.data?.detail || e.message));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1 className="title">TrustLens AI</h1>
      <p className="subtitle">Global Truth Engine</p>

      <div className="card">
        <input
          type="text"
          placeholder="Paste any URL (e.g. bbc.com)"
          className="input"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && check()}
        />
        <button onClick={check} disabled={loading} className="button">
          {loading ? "Analyzing..." : "Check Truth"}
        </button>

        {result && (
          <div className="result">
            <div className="score">Score: {result.score}/100</div>
            {result.evidence.map((e: any, i: number) => (
              <div key={i} className="evidence">
                <span>•</span>
                <div>
                  <strong>{e.title}:</strong> {e.summary}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <p className="footer">
        Powered by real-time WHOIS, SSL, and AI analysis.
      </p>
    </div>
  );
}

export default App;
