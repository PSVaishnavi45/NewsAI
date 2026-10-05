import React, { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function AIAnalyzer() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analyzeArticle = async () => {
    if (!text.trim()) {
      setError("Please enter a news article first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/ai/classify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      setResult(data);
    } catch (err) {
      console.error("Analysis error:", err);
      setError(
        "Unable to analyze the article. Please make sure the backend server is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const clearAnalysis = () => {
    setText("");
    setResult(null);
    setError("");
  };

  const formatConfidence = (confidence) => {
    const value = Number(confidence);

    if (value <= 1) {
      return (value * 100).toFixed(2);
    }

    return value.toFixed(2);
  };

  const getCategoryIcon = (category) => {
    const icons = {
      Technology: "💻",
      Sports: "⚽",
      Politics: "🏛️",
      Business: "💼",
      Entertainment: "🎬",
      Science: "🔬",
      Health: "🏥",
      World: "🌍",
      Education: "📚",
      Environment: "🌱",
    };

    return icons[category] || "📰";
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f7f7fc",
        padding: "40px 20px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: "1100px",
          margin: "0 auto",
        }}
      >
        {/* HEADER */}

        <div style={{ marginBottom: "30px" }}>
          <h1
            style={{
              fontSize: "38px",
              marginBottom: "10px",
              color: "#1f1f2e",
            }}
          >
            🤖 AI News Analyzer
          </h1>

          <p
            style={{
              color: "#6b6b7a",
              fontSize: "17px",
            }}
          >
            Analyze news articles using a multilingual Transformer-based AI
            model.
          </p>
        </div>

        {/* INPUT CARD */}

        <div
          style={{
            background: "white",
            borderRadius: "20px",
            padding: "30px",
            boxShadow: "0 10px 35px rgba(70, 50, 120, 0.08)",
            marginBottom: "35px",
          }}
        >
          <h2
            style={{
              marginTop: 0,
              color: "#252536",
            }}
          >
            📰 Enter News Article
          </h2>

          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste your news article here..."
            rows={9}
            style={{
              width: "100%",
              boxSizing: "border-box",
              border: "2px solid #e6e2f5",
              borderRadius: "14px",
              padding: "18px",
              fontSize: "16px",
              resize: "vertical",
              outline: "none",
              color: "#29293a",
              lineHeight: "1.6",
            }}
          />

          <div
            style={{
              marginTop: "18px",
              display: "flex",
              gap: "12px",
              alignItems: "center",
              flexWrap: "wrap",
            }}
          >
            <button
              onClick={analyzeArticle}
              disabled={loading}
              style={{
                border: "none",
                borderRadius: "12px",
                padding: "14px 25px",
                background: loading ? "#a99be8" : "#6d3df5",
                color: "white",
                fontSize: "16px",
                fontWeight: "bold",
                cursor: loading ? "not-allowed" : "pointer",
              }}
            >
              {loading ? "⏳ Analyzing..." : "✨ Analyze Article"}
            </button>

            <button
              onClick={clearAnalysis}
              style={{
                border: "1px solid #ddd8ef",
                borderRadius: "12px",
                padding: "14px 22px",
                background: "white",
                color: "#55556a",
                fontSize: "16px",
                cursor: "pointer",
              }}
            >
              Clear
            </button>
          </div>

          <p
            style={{
              color: "#77778a",
              fontSize: "13px",
              marginBottom: 0,
            }}
          >
            🔒 Your article is analyzed through your connected AI server.
          </p>

          {error && (
            <div
              style={{
                marginTop: "18px",
                padding: "14px 16px",
                background: "#fff0f0",
                border: "1px solid #ffd0d0",
                borderRadius: "10px",
                color: "#c62828",
              }}
            >
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* RESULTS */}

        {result && (
          <div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                marginBottom: "22px",
              }}
            >
              <h2
                style={{
                  margin: 0,
                  color: "#252536",
                }}
              >
                Analysis Results
              </h2>

              <span
                style={{
                  background: "#e6faef",
                  color: "#159447",
                  padding: "7px 12px",
                  borderRadius: "20px",
                  fontSize: "13px",
                  fontWeight: "bold",
                }}
              >
                ✓ COMPLETE
              </span>
            </div>

            {/* THREE RESULT CARDS */}

            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(250px, 1fr))",
                gap: "20px",
                marginBottom: "20px",
              }}
            >
              {/* CATEGORY */}

              <div
                style={{
                  background: "white",
                  borderRadius: "20px",
                  padding: "28px",
                  boxShadow: "0 8px 30px rgba(70, 50, 120, 0.07)",
                }}
              >
                <div
                  style={{
                    color: "#7d7890",
                    fontSize: "13px",
                    fontWeight: "bold",
                    letterSpacing: "1px",
                    marginBottom: "18px",
                  }}
                >
                  PREDICTED CATEGORY
                </div>

                <div
                  style={{
                    color: "#6134df",
                    fontSize: "27px",
                    fontWeight: "bold",
                  }}
                >
                  {getCategoryIcon(result.category)}{" "}
                  {result.category || "Unknown"}
                </div>
              </div>

              {/* CONFIDENCE */}

              <div
                style={{
                  background: "white",
                  borderRadius: "20px",
                  padding: "28px",
                  boxShadow: "0 8px 30px rgba(70, 50, 120, 0.07)",
                }}
              >
                <div
                  style={{
                    color: "#7d7890",
                    fontSize: "13px",
                    fontWeight: "bold",
                    letterSpacing: "1px",
                    marginBottom: "18px",
                  }}
                >
                  MODEL CONFIDENCE
                </div>

                <div
                  style={{
                    color: "#6134df",
                    fontSize: "34px",
                    fontWeight: "bold",
                    marginBottom: "15px",
                  }}
                >
                  {formatConfidence(result.confidence)}%
                </div>

                <div
                  style={{
                    width: "100%",
                    height: "8px",
                    background: "#ebe8f5",
                    borderRadius: "10px",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: `${Math.min(
                        Number(result.confidence) <= 1
                          ? Number(result.confidence) * 100
                          : Number(result.confidence),
                        100
                      )}%`,
                      height: "100%",
                      background: "#7544ed",
                      borderRadius: "10px",
                    }}
                  />
                </div>
              </div>

              {/* LANGUAGE */}

              <div
                style={{
                  background: "white",
                  borderRadius: "20px",
                  padding: "28px",
                  boxShadow: "0 8px 30px rgba(70, 50, 120, 0.07)",
                }}
              >
                <div
                  style={{
                    color: "#7d7890",
                    fontSize: "13px",
                    fontWeight: "bold",
                    letterSpacing: "1px",
                    marginBottom: "18px",
                  }}
                >
                  LANGUAGE
                </div>

                <div
                  style={{
                    color: "#252536",
                    fontSize: "27px",
                    fontWeight: "bold",
                  }}
                >
                  🌐 {result.language || "Unknown"}
                </div>
              </div>
            </div>

            {/* KEYWORDS */}

            <div
              style={{
                background: "white",
                borderRadius: "20px",
                padding: "28px",
                boxShadow: "0 8px 30px rgba(70, 50, 120, 0.07)",
              }}
            >
              <h3
                style={{
                  marginTop: 0,
                  color: "#252536",
                  fontSize: "20px",
                }}
              >
                🔑 Important Keywords
              </h3>

              {result.important_keywords &&
              result.important_keywords.length > 0 ? (
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "10px",
                  }}
                >
                  {result.important_keywords.map((keyword, index) => (
                    <span
                      key={`${keyword}-${index}`}
                      style={{
                        background: "#f0ebff",
                        color: "#5c35d5",
                        border: "1px solid #e0d5ff",
                        padding: "9px 15px",
                        borderRadius: "20px",
                        fontSize: "14px",
                        fontWeight: "600",
                      }}
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              ) : (
                <p style={{ color: "#77778a" }}>
                  No important keywords found.
                </p>
              )}
            </div>

            {/* FOOTER */}

            <div
              style={{
                textAlign: "center",
                color: "#9995aa",
                fontSize: "13px",
                marginTop: "25px",
                paddingBottom: "30px",
              }}
            >
              Powered by a multilingual Transformer-based NLP model
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AIAnalyzer;