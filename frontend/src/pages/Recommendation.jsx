import React, { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function Recommendations() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_URL}/api/recommendations/`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch recommendations");
      }

      const data = await response.json();

      console.log("Recommendation API:", data);

      /*
       * Your backend may return:
       *
       * { recommendations: [...] }
       * or
       * { articles: [...] }
       * or
       * [...]
       */

      if (Array.isArray(data)) {
        setArticles(data);
      } else if (Array.isArray(data.recommendations)) {
        setArticles(data.recommendations);
      } else if (Array.isArray(data.articles)) {
        setArticles(data.articles);
      } else {
        setArticles([]);
      }
    } catch (err) {
      console.error("Recommendation error:", err);
      setError("Unable to load recommendations.");
    } finally {
      setLoading(false);
    }
  };

  const getSourceUrl = (article) => {
    return (
      article.source_url ||
      article.url ||
      article.sourceUrl ||
      article.link ||
      "#"
    );
  };

  const getSourceName = (article) => {
    return (
      article.source_name ||
      article.source ||
      article.sourceName ||
      "News Source"
    );
  };

  const getDescription = (article) => {
    return (
      article.description ||
      article.content ||
      article.summary ||
      "No description available."
    );
  };

  const getCategory = (article) => {
    return article.category || "News";
  };

  const getLanguage = (article) => {
    return article.language || "English";
  };

  return (
    <div className="recommendations-page">

      {/* HEADER */}
      <section
        style={{
          padding: "50px 6%",
          background:
            "linear-gradient(135deg, #f7f4ff 0%, #ffffff 100%)",
        }}
      >
        <div style={{ maxWidth: "1200px", margin: "auto" }}>

          <div
            style={{
              display: "inline-block",
              padding: "8px 16px",
              borderRadius: "30px",
              background: "#eee7ff",
              color: "#683cff",
              fontWeight: "700",
              fontSize: "14px",
              marginBottom: "20px",
            }}
          >
            ✨ AI RECOMMENDATIONS
          </div>

          <h1
            style={{
              fontSize: "48px",
              margin: "0 0 15px",
              fontWeight: "600",
            }}
          >
            Recommended for you
          </h1>

          <p
            style={{
              fontSize: "18px",
              color: "#777",
              maxWidth: "700px",
              lineHeight: "1.7",
            }}
          >
            Discover related multilingual news based on topics,
            categories and semantic similarity.
          </p>

        </div>
      </section>

      {/* CONTENT */}
      <section
        style={{
          padding: "30px 6% 80px",
          background: "#f7f7fb",
          minHeight: "500px",
        }}
      >
        <div style={{ maxWidth: "1200px", margin: "auto" }}>

          {/* LOADING */}
          {loading && (
            <div
              style={{
                textAlign: "center",
                padding: "80px 20px",
                fontSize: "20px",
                color: "#683cff",
              }}
            >
              <div style={{ fontSize: "40px", marginBottom: "15px" }}>
                ✨
              </div>

              <strong>AI is finding recommendations...</strong>

              <p style={{ color: "#888" }}>
                Please wait while we load related news.
              </p>
            </div>
          )}

          {/* ERROR */}
          {!loading && error && (
            <div
              style={{
                background: "#fff",
                padding: "40px",
                borderRadius: "20px",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "40px" }}>⚠️</div>

              <h2>Recommendations unavailable</h2>

              <p style={{ color: "#777" }}>
                {error}
              </p>

              <button
                onClick={fetchRecommendations}
                style={{
                  padding: "12px 25px",
                  border: "none",
                  borderRadius: "10px",
                  background: "#683cff",
                  color: "white",
                  fontWeight: "600",
                  cursor: "pointer",
                }}
              >
                Try Again
              </button>
            </div>
          )}

          {/* NO RESULTS */}
          {!loading &&
            !error &&
            articles.length === 0 && (
              <div
                style={{
                  background: "#fff",
                  padding: "60px",
                  borderRadius: "20px",
                  textAlign: "center",
                }}
              >
                <div style={{ fontSize: "50px" }}>📰</div>

                <h2>No recommendations available</h2>

                <p style={{ color: "#777" }}>
                  The recommendation API did not return any articles.
                </p>

                <button
                  onClick={fetchRecommendations}
                  style={{
                    padding: "12px 25px",
                    border: "none",
                    borderRadius: "10px",
                    background: "#683cff",
                    color: "white",
                    fontWeight: "600",
                    cursor: "pointer",
                  }}
                >
                  Refresh
                </button>
              </div>
            )}

          {/* RECOMMENDATION CARDS */}
          {!loading &&
            !error &&
            articles.length > 0 && (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(320px, 1fr))",
                  gap: "25px",
                }}
              >
                {articles.map((article, index) => {

                  const sourceUrl = getSourceUrl(article);

                  return (
                    <div
                      key={
                        article.id ||
                        article.article_id ||
                        index
                      }
                      style={{
                        background: "#fff",
                        borderRadius: "22px",
                        overflow: "hidden",
                        boxShadow:
                          "0 5px 25px rgba(70,50,120,0.08)",
                        border:
                          "1px solid #eee8ff",
                      }}
                    >

                      {/* TOP */}
                      <div
                        style={{
                          background:
                            "linear-gradient(135deg,#eee7ff,#f8f6ff)",
                          padding: "25px",
                          minHeight: "100px",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            justifyContent:
                              "space-between",
                            alignItems: "center",
                          }}
                        >
                          <span
                            style={{
                              background: "#fff",
                              padding: "7px 14px",
                              borderRadius: "20px",
                              color: "#683cff",
                              fontWeight: "700",
                              fontSize: "13px",
                            }}
                          >
                            {getCategory(article)}
                          </span>

                          <span
                            style={{
                              background: "#e4fff3",
                              color: "#159a68",
                              padding: "7px 12px",
                              borderRadius: "20px",
                              fontSize: "12px",
                              fontWeight: "700",
                            }}
                          >
                            AI
                          </span>
                        </div>
                      </div>

                      {/* BODY */}
                      <div style={{ padding: "25px" }}>

                        <div
                          style={{
                            color: "#999",
                            fontSize: "13px",
                            marginBottom: "12px",
                          }}
                        >
                          {getLanguage(article)}
                          {" • "}
                          {getSourceName(article)}
                        </div>

                        <h2
                          style={{
                            fontSize: "21px",
                            lineHeight: "1.4",
                            marginBottom: "15px",
                          }}
                        >
                          {article.title ||
                            "Recommended News"}
                        </h2>

                        <p
                          style={{
                            color: "#777",
                            lineHeight: "1.6",
                            fontSize: "14px",
                            minHeight: "65px",
                          }}
                        >
                          {getDescription(article)}
                        </p>

                        <div
                          style={{
                            borderTop:
                              "1px solid #eee",
                            marginTop: "20px",
                            paddingTop: "18px",
                          }}
                        >

                          <div
                            style={{
                              color: "#683cff",
                              fontSize: "14px",
                              fontWeight: "600",
                              marginBottom: "15px",
                            }}
                          >
                            ✨ AI Recommended
                          </div>

                          {sourceUrl !== "#" ? (
                            <a
                              href={sourceUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{
                                display: "block",
                                textDecoration: "none",
                                textAlign: "center",
                                padding: "13px",
                                borderRadius: "12px",
                                background: "#eee8ff",
                                color: "#683cff",
                                fontWeight: "700",
                              }}
                            >
                              🔗 Read Original Article →
                            </a>
                          ) : (
                            <div
                              style={{
                                padding: "13px",
                                borderRadius: "12px",
                                background: "#f1f1f1",
                                color: "#999",
                                textAlign: "center",
                              }}
                            >
                              Original source unavailable
                            </div>
                          )}

                        </div>

                      </div>
                    </div>
                  );
                })}
              </div>
            )}

        </div>
      </section>
    </div>
  );
}

export default Recommendations;