import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
const API_BASE = "http://localhost:8000";

const categories = [
  "All",
  "Politics",
  "Business",
  "Technology",
  "Sports",
  "Health",
  "Entertainment",
  "Education",
  "Culture & Religion"
];

const languages = [
  "All Languages",
  "English",
  "Hindi",
  "Telugu",
  "Tamil",
  "Kannada",
  "Malayalam",
  "Bengali",
  "Marathi",
];

const translationLanguages = [
  "English",
  "Hindi",
  "Telugu",
  "Tamil",
  "Kannada",
  "Malayalam",
  "Bengali",
  "Marathi",
];

const icons = {
  Politics: "🏛️",
  Business: "📈",
  Technology: "🤖",
  Sports: "🏆",
  Health: "🩺",
  Entertainment: "🎬",
  Education: "🎓",
  Science: "🔬",
};

function getIcon(category) {
  return icons[category] || "📰";
}

function formatTime(value) {
  if (!value) return "Recently";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Recently";
  }

  const diff = Math.max(0, Date.now() - date.getTime());
  const minutes = Math.floor(diff / 60000);

  if (minutes < 1) return "Just now";

  if (minutes < 60) {
    return `${minutes} min ago`;
  }

  const hours = Math.floor(minutes / 60);

  if (hours < 24) {
    return `${hours} hr ago`;
  }

  const days = Math.floor(hours / 24);

  if (days < 7) {
    return `${days} day${days > 1 ? "s" : ""} ago`;
  }

  return date.toLocaleDateString();
}

function normalizeArticle(article, index) {
  if (!article || typeof article !== "object") {
    return null;
  }

  const sourceUrl =
    article.source_url ||
    article.sourceUrl ||
    article.url ||
    "";

  const category =
    article.category ||
    "Technology";

  let confidence = null;

  if (typeof article.confidence === "number") {
    confidence =
      article.confidence <= 1
        ? article.confidence * 100
        : article.confidence;
  }

  return {
    id:
      article.id ||
      `${article.source_name || article.source || "news"}-${index}`,

    title:
      article.title ||
      "Untitled news article",

    description:
      article.description ||
      article.content ||
      article.summary ||
      "No description available.",

    category,

    language:
      article.language ||
      "English",

    source:
      article.source_name ||
      article.source ||
      "News Source",

    source_url: sourceUrl,
    url: sourceUrl,

    published_at:
      article.published_at ||
      article.publishedAt ||
      "",

    author:
      article.author ||
      "",

    confidence,

    icon: getIcon(category),

    time: formatTime(
      article.published_at ||
      article.publishedAt
    ),
  };
}

async function getJson(response) {
  const text = await response.text();

  if (!text) {
    throw new Error(
      `Empty response from server (${response.status})`
    );
  }

  try {
    return JSON.parse(text);
  } catch {
    console.error(
      "Server returned non-JSON response:",
      text
    );

    throw new Error(
      "Backend returned invalid JSON."
    );
  }
}

function News() {
  const navigate = useNavigate();
  const [newsArticles, setNewsArticles] = useState([]);

  const [selectedCategory, setSelectedCategory] =
    useState("All");

  const [selectedLanguage, setSelectedLanguage] =
    useState("All Languages");

  const [search, setSearch] = useState("");

  const [newsLoading, setNewsLoading] =
    useState(true);

  const [newsError, setNewsError] =
    useState("");

  const [lastUpdated, setLastUpdated] =
    useState("");

  const [selectedArticle, setSelectedArticle] =
    useState(null);

  const [activeNav, setActiveNav] =
    useState("news-feed");

  const [analysisData, setAnalysisData] =
    useState(null);

  const [analysisLoading, setAnalysisLoading] =
    useState(false);

  const [summary, setSummary] = useState("");

  const [summaryLoading, setSummaryLoading] =
    useState(false);

  const [summaryError, setSummaryError] =
    useState("");

  const [showTranslation, setShowTranslation] =
    useState(false);

  const [translationLanguage, setTranslationLanguage] =
    useState("Telugu");

  const [translation, setTranslation] =
    useState("");

  const [translationLoading, setTranslationLoading] =
    useState(false);

  const [translationError, setTranslationError] =
    useState("");

  const [recommendations, setRecommendations] =
    useState([]);

  const [recommendationLoading, setRecommendationLoading] =
    useState(false);

  const [recommendationError, setRecommendationError] =
    useState("");

  /* =========================================================
     FETCH NEWS
  ========================================================= */

  const fetchNews = async () => {
    setNewsLoading(true);
    setNewsError("");

    try {
      const response = await fetch(
        `${API_BASE}/api/news/`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
          },
        }
      );

      const data = await getJson(response);

      console.log("NEWS API RESPONSE:", data);

      if (!response.ok) {
        throw new Error(
          data?.detail ||
          data?.error ||
          `News API failed with status ${response.status}`
        );
      }

      /*
        Your backend returns:

        {
          success: true,
          count: 50,
          updated_at: "...",
          languages: [...],
          articles: [...]
        }
      */

      let rawArticles = [];

      if (Array.isArray(data?.articles)) {
        rawArticles = data.articles;
      } else if (Array.isArray(data)) {
        rawArticles = data;
      } else if (Array.isArray(data?.data)) {
        rawArticles = data.data;
      }

      const articles = rawArticles
        .map((article, index) =>
          normalizeArticle(article, index)
        )
        .filter(Boolean);

      console.log(
        "NORMALIZED NEWS ARTICLES:",
        articles
      );

      setNewsArticles(articles);

      setLastUpdated(
        data?.updated_at ||
        data?.updatedAt ||
        new Date().toISOString()
      );

      if (articles.length === 0) {
        setNewsError(
          "The backend responded successfully, but no articles were returned."
        );
      }
    } catch (error) {
      console.error(
        "NEWS FETCH ERROR:",
        error
      );

      setNewsArticles([]);

      let message =
        "Unable to load live news.";

      if (
        error?.message?.includes(
          "Failed to fetch"
        )
      ) {
        message =
          "Cannot connect to the FastAPI backend. Make sure it is running on port 8000 and CORS is enabled.";
      } else if (
        error?.message
      ) {
        message =
          error.message;
      }

      setNewsError(message);
    } finally {
      setNewsLoading(false);
    }
  };

  /* =========================================================
     INITIAL LOAD
  ========================================================= */

  useEffect(() => {
    fetchNews();

    const timer = setInterval(
      fetchNews,
      5 * 60 * 1000
    );

    return () => {
      clearInterval(timer);
    };
  }, []);

  /* =========================================================
     FILTER
  ========================================================= */

  const filteredNews = useMemo(() => {
    const query =
      search.trim().toLowerCase();

    return newsArticles.filter(
      (article) => {
        const categoryMatch =
          selectedCategory === "All" ||
          article.category ===
            selectedCategory;

        const languageMatch =
          selectedLanguage ===
            "All Languages" ||
          article.language ===
            selectedLanguage;

        const title =
          String(article.title || "")
            .toLowerCase();

        const description =
          String(article.description || "")
            .toLowerCase();

        const source =
          String(article.source || "")
            .toLowerCase();

        const searchMatch =
          !query ||
          title.includes(query) ||
          description.includes(query) ||
          source.includes(query);

        return (
          categoryMatch &&
          languageMatch &&
          searchMatch
        );
      }
    );
  }, [
    newsArticles,
    selectedCategory,
    selectedLanguage,
    search,
  ]);

  /* =========================================================
     NAVIGATION
  ========================================================= */

  const scrollToSection = (id) => {
    setActiveNav(id);

    const element =
      document.getElementById(id);

    if (element) {
      element.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  };

  const handleSearch = () => {
    scrollToSection("news-feed");
  };

  /* =========================================================
     RESET
  ========================================================= */

  const resetAnalysisState = () => {
    setAnalysisData(null);
    setAnalysisLoading(false);

    setSummary("");
    setSummaryLoading(false);
    setSummaryError("");

    setShowTranslation(false);
    setTranslation("");
    setTranslationLoading(false);
    setTranslationError("");

    setTranslationLanguage("Telugu");
  };

  /* =========================================================
     ANALYZE
  ========================================================= */

  const openAnalysis = async (article) => {
    setSelectedArticle(article);

    resetAnalysisState();

    setAnalysisLoading(true);

    const articleText =
      `${article.title}. ${article.description}`;

    try {
      const response = await fetch(
        `${API_BASE}/api/ai/classify`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
            Accept: "application/json",
          },

          body: JSON.stringify({
            text: articleText,
          }),
        }
      );

      const data =
        await getJson(response);

      if (!response.ok) {
        throw new Error(
          data?.detail ||
          data?.error ||
          "Article analysis failed"
        );
      }

      setAnalysisData(data);
    } catch (error) {
      console.error(
        "Analysis Error:",
        error
      );

      setAnalysisData({
        category:
          article.category ||
          "Unknown",

        confidence:
          article.confidence
            ? article.confidence / 100
            : 0,

        language:
          article.language ||
          "Unknown",

        important_keywords: [],

        explanation:
          "The AI analysis service could not be reached.",
      });
    } finally {
      setAnalysisLoading(false);
    }
  };

  /* =========================================================
     CLOSE ANALYSIS
  ========================================================= */

  const closeAnalysis = () => {
    setSelectedArticle(null);
    resetAnalysisState();
  };

  /* =========================================================
     SUMMARY
  ========================================================= */

  const generateSummary = async () => {
    if (!selectedArticle) {
      return;
    }

    setSummaryLoading(true);
    setSummary("");
    setSummaryError("");

    try {
      const response = await fetch(
        `${API_BASE}/api/ai/summarize`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
            Accept: "application/json",
          },

          body: JSON.stringify({
            title:
              selectedArticle.title,

            text:
              selectedArticle.description,
          }),
        }
      );

      const data =
        await getJson(response);
      console.log("SUMMARY API RESPONSE:", data);

      if (!response.ok) {
        throw new Error(
          data?.detail ||
          data?.error ||
          "Failed to generate summary"
        );
      }

      const result =
        data?.summary ||
        data?.result ||
        "";

      if (
        result &&
        !result.startsWith(
          "Unable to generate"
        )
      ) {
        setSummary(result);
      } else {
        setSummaryError(
          result ||
          "The AI did not return a summary."
        );
      }
    } catch (error) {
      console.error(
        "Summary Error:",
        error
      );

      setSummaryError(
        error?.message ||
        "Unable to generate AI summary. Please make sure the backend is running."
      );
    } finally {
      setSummaryLoading(false);
    }
  };

  /* =========================================================
     TRANSLATION
  ========================================================= */

  const openTranslation = () => {
    setShowTranslation(true);
    setTranslation("");
    setTranslationError("");
  };

  const closeTranslation = () => {
    setShowTranslation(false);
    setTranslation("");
    setTranslationError("");
    setTranslationLoading(false);
  };

  const translateArticle = async () => {
    if (!selectedArticle) {
      return;
    }

    setTranslationLoading(true);
    setTranslation("");
    setTranslationError("");

    try {
      const response = await fetch(
        `${API_BASE}/api/ai/translate`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
            Accept: "application/json",
          },

          body: JSON.stringify({
  text:
    `${selectedArticle.title}. ${selectedArticle.description}`,

  target_language:
    translationLanguage,

  source_language:
    selectedArticle.language || "English",
}),
        }
      );

      const data =
        await getJson(response);

      if (!response.ok) {
        throw new Error(
          data?.error ||
          data?.detail ||
          "Translation failed"
        );
      }

      const translatedText =
        data?.translation ||
        data?.translated_text ||
        data?.result ||
        "";

      if (
        translatedText &&
        !translatedText.startsWith(
          "Unable to translate"
        ) &&
        !translatedText.startsWith(
          "Translation from this source language"
        ) &&
        !translatedText.startsWith(
          "Selected language is not supported"
        )
      ) {
        setTranslation(
          translatedText
        );
      } else {
        setTranslationError(
          translatedText ||
          "Unable to translate the article."
        );
      }
    } catch (error) {
      console.error(
        "Translation Error:",
        error
      );

      setTranslationError(
        error?.message ||
        "Unable to translate the article. Please make sure the backend is running."
      );
    } finally {
      setTranslationLoading(false);
    }
  };

  /* =========================================================
     RECOMMENDATIONS
  ========================================================= */

  const fetchRecommendations =
    async () => {
      setRecommendationLoading(true);
      setRecommendationError("");

      try {
        const response =
          await fetch(
            `${API_BASE}/api/recommendations/`,
            {
              method: "GET",
              headers: {
                Accept:
                  "application/json",
              },
            }
          );

        const data =
          await getJson(response);

        if (!response.ok) {
          throw new Error(
            data?.detail ||
            data?.error ||
            "Unable to load recommendations"
          );
        }

        const result =
          Array.isArray(
            data?.recommendations
          )
            ? data.recommendations
            : Array.isArray(data)
            ? data
            : [];

        setRecommendations(result);
      } catch (error) {
        console.error(
          "Recommendation Error:",
          error
        );

        setRecommendationError(
          error?.message ||
          "Unable to connect to the recommendation server."
        );
      } finally {
        setRecommendationLoading(
          false
        );
      }
    };

  const handleRecommendations = () => {
    scrollToSection(
      "recommendations"
    );

    if (
      recommendations.length === 0
    ) {
      fetchRecommendations();
    }
  };

  /* =========================================================
     RENDER
  ========================================================= */

  return (
    <div className="news-page">

      {/* NAVBAR */}

      <header className="navbar">

        <div
          className="brand"
          onClick={() =>
            scrollToSection(
              "news-feed"
            )
          }
        >
          <div className="brand-logo">
            N
          </div>

          <div>
            <h1>NewsAI</h1>

            <span>
              Intelligent News •
              Explained
            </span>
          </div>
        </div>

        <nav>

          <button
            className={
              activeNav ===
              "news-feed"
                ? "nav-link active"
                : "nav-link"
            }
            onClick={() =>
              scrollToSection(
                "news-feed"
              )
            }
          >
            News Feed
          </button>

          <button
            className={
              activeNav ===
              "recommendations"
                ? "nav-link active"
                : "nav-link"
            }
            onClick={
              handleRecommendations
            }
          >
            Recommendations
          </button>

          <button
            className={
              activeNav ===
              "trending"
                ? "nav-link active"
                : "nav-link"
            }
            onClick={() =>
              scrollToSection(
                "trending"
              )
            }
          >
            Trending
          </button>

          <button
            className={
              activeNav ===
              "analytics"
                ? "nav-link active"
                : "nav-link"
            }
            onClick={() =>
              scrollToSection(
                "analytics"
              )
            }
          >
            Analytics
          </button>
          <button
  className="nav-link"
  onClick={() => navigate("/login")}
>
  Login
</button>

        </nav>

        <button className="profile-button">
          👤
        </button>

      </header>

      {/* HERO */}

      <section className="hero">

        <div className="hero-content">

          <div className="hero-badge">
            ✨ AI-Powered
            Multilingual
            Intelligence
          </div>

          <h2>
            Understand the news.
            <br />

            <span>
              Not just read it.
            </span>
          </h2>

          <p>
            Discover multilingual
            news, understand why AI
            classified it, and receive
            recommendations tailored
            to your interests.
          </p>

          <div className="search-box">

            <span>🔎</span>

            <input
              type="text"
              placeholder="Search live news..."
              value={search}
              onChange={(e) =>
                setSearch(
                  e.target.value
                )
              }
              onKeyDown={(e) => {
                if (
                  e.key === "Enter"
                ) {
                  handleSearch();
                }
              }}
            />

            <button
              onClick={
                handleSearch
              }
            >
              Search
            </button>

          </div>

          <div className="live-status">

            <span className="live-dot"></span>

            Live news feed

            {lastUpdated && (
              <span>
                • Updated{" "}
                {formatTime(
                  lastUpdated
                )}
              </span>
            )}

            <button
              onClick={fetchNews}
              disabled={
                newsLoading
              }
            >
              {newsLoading
                ? "Refreshing..."
                : "↻ Refresh"}
            </button>

          </div>

        </div>

        <div className="hero-ai-card">

          <div className="ai-card-top">

            <div className="ai-icon">
              ✦
            </div>

            <div>
              <strong>
                AI News Intelligence
              </strong>

              <span>
                Real-time analysis
              </span>
            </div>

            <div className="status-dot"></div>

          </div>

          <div className="ai-stat">

            <div>
              <strong>8</strong>
              <span>Categories</span>
            </div>

            <div>
              <strong>8+</strong>
              <span>Languages</span>
            </div>

            <div>
              <strong>AI</strong>
              <span>Analysis</span>
            </div>

          </div>

          <div className="ai-line">
            <span></span>
          </div>

          <p>
            ✓ Explainable predictions
            <br />
            ✓ Cross-language translation
            <br />
            ✓ Real-time news sources
            <br />
            ✓ Semantic understanding
          </p>

        </div>

      </section>

      {/* NEWS FEED */}

      <main
        className="content"
        id="news-feed"
      >

        <div className="section-header">

          <div>

            <span className="section-label">
              PERSONALIZED FEED
            </span>

            <h2>
              Latest Intelligence
            </h2>

            <p>
              Live news collected from
              trusted RSS sources
            </p>

          </div>

          <select
            value={
              selectedLanguage
            }
            onChange={(e) =>
              setSelectedLanguage(
                e.target.value
              )
            }
          >
            {languages.map(
              (language) => (
                <option
                  key={language}
                  value={language}
                >
                  {language}
                </option>
              )
            )}
          </select>

        </div>

        <div className="category-row">

          {categories.map(
            (category) => (
              <button
                key={category}
                className={
                  selectedCategory ===
                  category
                    ? "category active-category"
                    : "category"
                }
                onClick={() =>
                  setSelectedCategory(
                    category
                  )
                }
              >
                {category}
              </button>
            )
          )}

        </div>

        {/* ERROR */}

        {newsError && (
          <div className="news-error">

            <strong>
              ⚠️ Live News Error
            </strong>

            <p>
              {newsError}
            </p>

            <button
              onClick={fetchNews}
              disabled={newsLoading}
            >
              {newsLoading
                ? "Trying..."
                : "Try Again"}
            </button>

          </div>
        )}

        {/* LOADING */}

        {newsLoading &&
          newsArticles.length ===
            0 && (
            <div className="news-loading">

              <div className="spinner"></div>

              <h3>
                Loading live news...
              </h3>

              <p>
                Fetching the latest
                articles.
              </p>

            </div>
          )}

        {/* NEWS GRID */}

        {!newsLoading &&
          filteredNews.length > 0 && (
          <div className="news-grid">

            {filteredNews.map(
              (article) => (
                <article
                  className="news-card"
                  key={article.id}
                >

                  <div className="news-image">

                    <span>
                      {article.icon}
                    </span>

                    <div className="category-badge">
                      {article.category}
                    </div>

                    <div className="live-badge">
                      LIVE
                    </div>

                  </div>

                  <div className="news-body">

                    <div className="article-meta">

                      <span>
                        {article.language}
                      </span>

                      <span>•</span>

                      <span>
                        {article.time}
                      </span>

                    </div>

                    <h3>
                      {article.title}
                    </h3>

                    <p>
                      {article.description}
                    </p>

                    <div className="source">

                      <span>●</span>

                      {article.source}

                    </div>

                    <div className="original-source">

                      {article.source_url ? (
                        <a
                          href={
                            article.source_url
                          }
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          🔗 Read Original Article →
                        </a>
                      ) : (
                        <span>
                          Original source unavailable
                        </span>
                      )}

                    </div>

                    <div className="card-footer">

                      <button
                        className="analyze-button"
                        onClick={() =>
                          openAnalysis(
                            article
                          )
                        }
                      >
                        Analyze →
                      </button>

                    </div>

                  </div>

                </article>
              )
            )}

          </div>
        )}

        {/* NO RESULTS */}

        {!newsLoading &&
          filteredNews.length ===
            0 &&
          !newsError && (
            <div className="no-results">

              <div>🔎</div>

              <h3>
                No articles found
              </h3>

              <p>
                Try another search,
                language or category.
              </p>

            </div>
          )}

        {/* BOTTOM */}

        <section className="bottom-section">

          <div
            className="trending-card"
            id="trending"
          >

            <div className="section-label">
              TRENDING NOW
            </div>

            <h2>
              What's happening
            </h2>

            <div className="trend-list">

              <div>
                <span>#01</span>

                <strong>
                  Artificial Intelligence
                </strong>

                <small>
                  Technology
                </small>
              </div>

              <div>
                <span>#02</span>

                <strong>
                  Technology Innovation
                </strong>

                <small>
                  Technology
                </small>
              </div>

              <div>
                <span>#03</span>

                <strong>
                  Digital Economy
                </strong>

                <small>
                  Business
                </small>
              </div>

            </div>

          </div>

          <div
            className="recommendation-card"
            id="recommendations"
          >

            <div className="recommendation-icon">
              ✦
            </div>

            <div>

              <span className="section-label">
                AI RECOMMENDATION
              </span>

              <h2>
                Recommended for you
              </h2>

              <p>
                Recommendations are
                based on semantic
                similarity, topics and
                multilingual news
                intelligence.
              </p>

              <button
                onClick={
                  fetchRecommendations
                }
                disabled={
                  recommendationLoading
                }
              >
                {recommendationLoading
                  ? "Loading recommendations..."
                  : "Explore recommendations →"}
              </button>

            </div>

          </div>

        </section>

        {recommendationError && (
          <p className="recommendation-error">
            {recommendationError}
          </p>
        )}

        {recommendations.length >
          0 && (
          <section className="recommendations-section">

            <div className="recommendations-grid">

              {recommendations.map(
                (item, index) => (
                  <div
                    className="recommendation-item"
                    key={
                      item.id ||
                      index
                    }
                  >

                    <div className="recommendation-item-top">

                      <span>🤖</span>

                      <strong>
                        {item.category ||
                          "News"}
                      </strong>

                    </div>

                    <h3>
                      {item.title ||
                        "Recommended article"}
                    </h3>

                    <p>
                      🌐{" "}
                      {item.language ||
                        "English"}
                    </p>

                    <div className="similarity">

                      AI Similarity:{" "}

                      {Math.round(
                        Number(
                          item.similarity ||
                          0
                        ) * 100
                      )}
                      %

                    </div>

                  </div>
                )
              )}

            </div>

          </section>
        )}

        {/* ANALYTICS */}

        <section
          className="analytics-section"
          id="analytics"
        >

          <span className="section-label">
            PLATFORM ANALYTICS
          </span>

          <h2>
            News Intelligence
            Analytics
          </h2>

          <p className="analytics-description">
            Overview of the
            AI-powered multilingual
            news intelligence platform.
          </p>

          <div className="analytics-grid">

            <div className="analytics-card">
              <strong>8</strong>
              <span>News Categories</span>
            </div>

            <div className="analytics-card">
              <strong>8+</strong>
              <span>Languages</span>
            </div>

            <div className="analytics-card">
              <strong>
                {newsArticles.length}
              </strong>
              <span>Live Articles</span>
            </div>

            <div className="analytics-card">
              <strong>AI</strong>
              <span>Analysis Engine</span>
            </div>

          </div>

          <div className="analytics-info">

            <div>
              <span>🤖</span>

              <h3>
                Transformer AI
              </h3>

              <p>
                Multilingual zero-shot
                news classification.
              </p>
            </div>

            <div>
              <span>💡</span>

              <h3>
                Explainable AI
              </h3>

              <p>
                Keywords and
                explanations support
                predictions.
              </p>
            </div>

            <div>
              <span>🌐</span>

              <h3>
                Translation
              </h3>

              <p>
                Articles can be
                translated into
                multiple Indian
                languages.
              </p>
            </div>

          </div>

        </section>

      </main>

      {/* ANALYSIS MODAL */}

      {selectedArticle && (

        <div
          className="modal-overlay"
          onClick={
            closeAnalysis
          }
        >

          <div
            className="analysis-modal"
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            <button
              className="close-button"
              onClick={
                closeAnalysis
              }
            >
              ×
            </button>

            <div className="modal-icon">
              {selectedArticle.icon}
            </div>

            <span className="section-label">
              AI ARTICLE ANALYSIS
            </span>

            <h2>
              {selectedArticle.title}
            </h2>

            {selectedArticle.source_url && (
              <a
                className="modal-source-link"
                href={
                  selectedArticle.source_url
                }
                target="_blank"
                rel="noopener noreferrer"
              >
                🔗 View original article on{" "}
                {selectedArticle.source}
              </a>
            )}

            {analysisLoading ? (

              <div className="analysis-loading">

                <div className="spinner"></div>

                <strong>
                  AI is analyzing the article...
                </strong>

                <p>
                  Please wait while
                  NewsAI analyzes the
                  article.
                </p>

              </div>

            ) : (

              <>

                <div className="analysis-result">

                  <div className="result-main">

                    <span>
                      Predicted Category
                    </span>

                    <strong>
                      {analysisData?.category ||
                        selectedArticle.category}
                    </strong>

                  </div>

                  <div className="result-confidence">

                    <span>
                      Confidence
                    </span>

                    <strong>

                      {analysisData
                        ? `${(
                            Number(
                              analysisData.confidence ||
                              0
                            ) * 100
                          ).toFixed(2)}%`
                        : "—"}

                    </strong>

                  </div>

                </div>



                <div className="keywords">

                  <h3>
                    🔑 Important signals
                  </h3>

                  <div>

                    {(analysisData
                      ?.important_keywords
                      ?.length
                      ? analysisData.important_keywords
                      : [
                          "news",
                          "context",
                          selectedArticle.category,
                        ]
                    ).map(
                      (
                        keyword,
                        index
                      ) => (
                        <span
                          key={index}
                        >
                          {keyword}
                        </span>
                      )
                    )}

                  </div>

                </div>

              </>

            )}

            {/* SUMMARY */}

            {summaryLoading && (

              <div className="ai-summary">

                <div className="summary-title">

                  <span className="summary-sparkle">
                    ✨
                  </span>

                  <h3>
                    Generating AI Summary
                  </h3>

                </div>

                <div className="loading-bar">
                  <span></span>
                </div>

                <p>
                  NewsAI is generating
                  a concise summary...
                </p>

              </div>

            )}

            {summary &&
              !summaryLoading && (

                <div className="ai-summary">

                  <div className="summary-title">

                    <span className="summary-sparkle">
                      ✨
                    </span>

                    <h3>
                      AI Summary
                    </h3>

                  </div>

                  <p>
                    {summary}
                  </p>

                </div>

              )}

            {summaryError && (

              <div className="ai-summary summary-error">

                <h3>
                  ⚠️ Summary Error
                </h3>

                <p>
                  {summaryError}
                </p>

              </div>

            )}

            {/* TRANSLATION */}

            {showTranslation && (

              <div className="translation-panel">

                <div className="translation-header">

                  <div>

                    <span className="translation-icon">
                      🌐
                    </span>

                    <div>

                      <h3>
                        Translate Article
                      </h3>

                      <p>
                        Choose your
                        preferred language
                      </p>

                    </div>

                  </div>

                  <button
                    className="translation-close"
                    onClick={
                      closeTranslation
                    }
                  >
                    ×
                  </button>

                </div>

                <div className="translation-controls">

                  <label>
                    Translate to
                  </label>

                  <select
                    value={
                      translationLanguage
                    }
                    onChange={(e) =>
                      setTranslationLanguage(
                        e.target.value
                      )
                    }
                    disabled={
                      translationLoading
                    }
                  >

                    {translationLanguages.map(
                      (language) => (
                        <option
                          key={language}
                          value={language}
                        >
                          {language}
                        </option>
                      )
                    )}

                  </select>

                  <button
                    className="do-translate-button"
                    onClick={
                      translateArticle
                    }
                    disabled={
                      translationLoading
                    }
                  >
                    {translationLoading
                      ? "⏳ Translating..."
                      : "🌐 Translate"}
                  </button>

                </div>

                {translationLoading && (

                  <div className="translation-loading">

                    <div className="translation-spinner">
                      ⟳
                    </div>

                    <strong>
                      AI is translating...
                    </strong>

                    <p>
                      Please wait while
                      NewsAI translates
                      the article.
                    </p>

                  </div>

                )}

                {translation &&
                  !translationLoading && (

                    <div className="translation-result">

                      <div className="translation-result-title">

                        <span>✓</span>

                        <strong>
                          Translated Article
                        </strong>

                      </div>

                      <p>
                        {translation}
                      </p>

                    </div>

                  )}

                {translationError && (

                  <div className="translation-error">

                    <strong>
                      ⚠️ Translation Error
                    </strong>

                    <p>
                      {translationError}
                    </p>

                  </div>

                )}

              </div>

            )}

            {/* BUTTONS */}

            <div className="modal-actions">

              <button
                onClick={
                  generateSummary
                }
                disabled={
                  summaryLoading
                }
                className="summary-button"
              >
                {summaryLoading
                  ? "⏳ Generating..."
                  : "✨ Generate Summary"}
              </button>

              <button
                onClick={
                  openTranslation
                }
                className="translate-button"
              >
                🌐 Translate
              </button>

              {selectedArticle.source_url && (

                <a
                  className="original-button"
                  href={
                    selectedArticle.source_url
                  }
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  🔗 Original Source
                </a>

              )}

              <button
                onClick={() => {
                  closeAnalysis();
                  handleRecommendations();
                }}
                className="recommend-button"
              >
                ❤️ Recommend Similar
              </button>

            </div>

          </div>

        </div>

      )}

      <style>{`

        * {
          box-sizing: border-box;
        }

        html {
          scroll-behavior: smooth;
        }

        body {
          margin: 0;
          font-family:
            Inter,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
          background: #f6f7fb;
          color: #171717;
        }

        button,
        input,
        select {
          font-family: inherit;
        }

        button,
        a {
          cursor: pointer;
        }

        .news-page {
          min-height: 100vh;
          background:
            radial-gradient(
              circle at 80% 0%,
              rgba(111, 76, 255, 0.1),
              transparent 35%
            ),
            #f6f7fb;
        }

        /* NAVBAR */

        .navbar {
          height: 78px;
          background:
            rgba(255,255,255,0.94);
          backdrop-filter:
            blur(20px);
          border-bottom:
            1px solid #e8e8ee;
          display: flex;
          align-items: center;
          padding: 0 6%;
          gap: 35px;
          position: sticky;
          top: 0;
          z-index: 20;
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-right: auto;
          cursor: pointer;
        }

        .brand-logo {
          width: 43px;
          height: 43px;
          border-radius: 13px;
          background:
            linear-gradient(
              135deg,
              #693cff,
              #a36cff
            );
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 22px;
          font-weight: 800;
          box-shadow:
            0 8px 20px
            rgba(105,60,255,0.25);
        }

        .brand h1 {
          margin: 0;
          font-size: 20px;
        }

        .brand span {
          color: #858595;
          font-size: 11px;
        }

        nav {
          display: flex;
          align-items: center;
          gap: 25px;
        }

        .nav-link {
          border: none;
          background: transparent;
          font-size: 14px;
          color: #777783;
          padding: 28px 0;
          border-bottom:
            2px solid transparent;
        }

        .nav-link:hover,
        .nav-link.active {
          color: #6538f5;
        }

        .nav-link.active {
          font-weight: 700;
          border-bottom-color:
            #6538f5;
        }

        .profile-button {
          border: 0;
          background: #f0edff;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          font-size: 17px;
        }

        /* HERO */

        .hero {
          max-width: 1250px;
          margin: auto;
          padding: 70px 30px 45px;
          display: grid;
          grid-template-columns:
            1.35fr 0.65fr;
          gap: 70px;
          align-items: center;
        }

        .hero-badge {
          display: inline-block;
          padding: 9px 15px;
          border-radius: 30px;
          background: #ece8ff;
          color: #6237e9;
          font-size: 12px;
          font-weight: 700;
          margin-bottom: 20px;
        }

        .hero h2 {
          font-size:
            clamp(45px, 5vw, 72px);
          line-height: 0.98;
          letter-spacing: -3px;
          margin: 0 0 25px;
        }

        .hero h2 span {
          color: #7040f8;
        }

        .hero-content > p {
          max-width: 650px;
          color: #6e6e7b;
          font-size: 17px;
          line-height: 1.7;
          margin-bottom: 30px;
        }

        /* SEARCH */

        .search-box {
          max-width: 650px;
          height: 62px;
          background: white;
          border:
            1px solid #e3e3ea;
          border-radius: 17px;
          display: flex;
          align-items: center;
          padding: 7px 8px 7px 20px;
          box-shadow:
            0 15px 35px
            rgba(30,20,70,0.08);
        }

        .search-box span {
          font-size: 20px;
          margin-right: 12px;
        }

        .search-box input {
          border: 0;
          outline: 0;
          flex: 1;
          font-size: 14px;
          min-width: 0;
        }

        .search-box button {
          border: 0;
          background: #683aff;
          color: white;
          padding: 13px 22px;
          border-radius: 12px;
          font-weight: 700;
        }

        .live-status {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-top: 14px;
          color: #777783;
          font-size: 12px;
          flex-wrap: wrap;
        }

        .live-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #31c48d;
          box-shadow:
            0 0 8px #31c48d;
        }

        .live-status button {
          border: 0;
          background: transparent;
          color: #683aff;
          font-weight: 700;
        }

        /* AI CARD */

        .hero-ai-card {
          background: #15121e;
          color: white;
          border-radius: 26px;
          padding: 28px;
          box-shadow:
            0 25px 50px
            rgba(40,20,80,0.22);
        }

        .ai-card-top {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .ai-icon {
          width: 42px;
          height: 42px;
          border-radius: 12px;
          background: #7345ff;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 22px;
        }

        .ai-card-top strong,
        .ai-card-top span {
          display: block;
        }

        .ai-card-top span {
          color: #9e9aa8;
          font-size: 12px;
          margin-top: 4px;
        }

        .status-dot {
          margin-left: auto;
          width: 9px;
          height: 9px;
          border-radius: 50%;
          background: #50e3a4;
          box-shadow:
            0 0 12px #50e3a4;
        }

        .ai-stat {
          display: grid;
          grid-template-columns:
            repeat(3, 1fr);
          margin: 40px 0 20px;
        }

        .ai-stat strong,
        .ai-stat span {
          display: block;
        }

        .ai-stat strong {
          font-size: 25px;
        }

        .ai-stat span {
          color: #98939f;
          font-size: 10px;
          margin-top: 5px;
        }

        .ai-line {
          height: 1px;
          background: #302c38;
          margin: 20px 0;
        }

        .ai-line span {
          display: block;
          width: 76%;
          height: 1px;
          background: #8b60ff;
        }

        .hero-ai-card p {
          color: #b3aebb;
          font-size: 13px;
          line-height: 2;
          margin: 0;
        }

        /* CONTENT */

        .content {
          max-width: 1250px;
          margin: auto;
          padding: 10px 30px 80px;
          scroll-margin-top: 95px;
        }

        .section-header {
          display: flex;
          align-items: end;
          justify-content: space-between;
          margin-bottom: 25px;
        }

        .section-label {
          color: #7040f8;
          font-size: 10px;
          letter-spacing: 1.5px;
          font-weight: 800;
        }

        .section-header h2 {
          margin: 7px 0;
          font-size: 31px;
        }

        .section-header p {
          color: #888894;
          margin: 0;
          font-size: 14px;
        }

        .section-header select {
          border:
            1px solid #dedee7;
          background: white;
          padding: 12px 16px;
          border-radius: 11px;
          outline: 0;
        }

        /* CATEGORIES */

        .category-row {
          display: flex;
          gap: 9px;
          overflow-x: auto;
          padding-bottom: 20px;
        }

        .category {
          white-space: nowrap;
          border:
            1px solid #e2e2e9;
          background: white;
          padding: 10px 17px;
          border-radius: 30px;
          color: #747481;
          font-size: 13px;
        }

        .active-category {
          background: #6b3cff;
          color: white;
          border-color:
            #6b3cff;
        }

        /* NEWS */

        .news-grid {
          display: grid;
          grid-template-columns:
            repeat(3, 1fr);
          gap: 22px;
        }

        .news-card {
          background: white;
          border:
            1px solid #e8e8ee;
          border-radius: 20px;
          overflow: hidden;
          transition:
            0.25s ease;
        }

        .news-card:hover {
          transform:
            translateY(-5px);
          box-shadow:
            0 20px 40px
            rgba(40,30,80,0.1);
        }

        .news-image {
          height: 155px;
          background:
            linear-gradient(
              135deg,
              #ece7ff,
              #f6f4ff
            );
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
        }

        .news-image > span {
          font-size: 58px;
        }

        .category-badge,
        .live-badge {
          position: absolute;
          top: 14px;
          padding: 6px 10px;
          border-radius: 8px;
          font-size: 10px;
          font-weight: 800;
        }

        .category-badge {
          left: 14px;
          background:
            rgba(255,255,255,0.92);
          color: #6037e4;
        }

        .live-badge {
          right: 14px;
          background: #e9fff5;
          color: #159267;
        }

        .news-body {
          padding: 20px;
        }

        .article-meta {
          display: flex;
          gap: 7px;
          color: #9999a5;
          font-size: 11px;
          margin-bottom: 10px;
        }

        .news-body h3 {
          margin: 0 0 10px;
          font-size: 17px;
          line-height: 1.35;
        }

        .news-body > p {
          color: #777783;
          font-size: 12px;
          line-height: 1.6;
          min-height: 58px;
        }

        .source {
          color: #777783;
          font-size: 11px;
          margin: 15px 0 8px;
          font-weight: 600;
        }

        .source span {
          color: #6b3cff;
          margin-right: 6px;
        }

        .original-source {
          margin: 8px 0 15px;
        }

        .original-source a {
          color: #6538f5;
          text-decoration: none;
          font-size: 12px;
          font-weight: 700;
        }

        .original-source a:hover {
          text-decoration: underline;
        }

        .original-source span {
          color: #999;
          font-size: 12px;
        }

        .card-footer {
          border-top:
            1px solid #eeeeF3;
          padding-top: 15px;
        }

        .analyze-button {
          width: 100%;
          border: 0;
          background: #f0ecff;
          color: #6438e8;
          padding: 11px;
          border-radius: 10px;
          font-weight: 700;
          font-size: 12px;
        }

        .analyze-button:hover {
          background: #6b3cff;
          color: white;
        }

        /* ERRORS */

        .news-error {
          background: #fff7f7;
          border:
            1px solid #ffd7d7;
          padding: 18px;
          border-radius: 15px;
          margin-bottom: 20px;
        }

        .news-error strong {
          color: #d64545;
        }

        .news-error p {
          color: #777;
          word-break: break-word;
        }

        .news-error button {
          border: 0;
          background: #6b3cff;
          color: white;
          padding: 9px 14px;
          border-radius: 9px;
          font-weight: 700;
        }

        .news-loading {
          background: white;
          border-radius: 20px;
          text-align: center;
          padding: 60px 20px;
          margin-bottom: 25px;
        }

        .spinner {
          width: 35px;
          height: 35px;
          border:
            4px solid #e5ddff;
          border-top:
            4px solid #683aff;
          border-radius: 50%;
          margin:
            0 auto 15px;
          animation:
            spin 1s linear infinite;
        }

        .no-results {
          background: white;
          text-align: center;
          padding: 60px;
          border-radius: 20px;
          margin-top: 20px;
        }

        /* BOTTOM */

        .bottom-section {
          display: grid;
          grid-template-columns:
            1fr 1fr;
          gap: 22px;
          margin-top: 35px;
        }

        .trending-card,
        .recommendation-card {
          background: white;
          border:
            1px solid #e7e7ee;
          border-radius: 20px;
          padding: 27px;
          scroll-margin-top: 100px;
        }

        .trending-card h2,
        .recommendation-card h2 {
          margin: 7px 0 20px;
          font-size: 24px;
        }

        .trend-list > div {
          display: grid;
          grid-template-columns:
            45px 1fr auto;
          align-items: center;
          padding: 14px 0;
          border-bottom:
            1px solid #eeeeF2;
        }

        .trend-list span,
        .trend-list small {
          color: #999;
          font-size: 11px;
        }

        .trend-list strong {
          font-size: 13px;
        }

        .recommendation-card {
          display: flex;
          gap: 20px;
          background:
            linear-gradient(
              135deg,
              #f3efff,
              #ffffff
            );
        }

        .recommendation-icon {
          width: 48px;
          height: 48px;
          min-width: 48px;
          border-radius: 15px;
          background: #6b3cff;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
        }

        .recommendation-card p {
          color: #777783;
          font-size: 13px;
          line-height: 1.6;
        }

        .recommendation-card button {
          border: 0;
          background: transparent;
          color: #683aff;
          font-weight: 700;
          padding: 0;
        }

        /* RECOMMENDATIONS */

        .recommendations-section {
          margin-top: 25px;
        }

        .recommendations-grid {
          display: grid;
          grid-template-columns:
            repeat(2, 1fr);
          gap: 20px;
        }

        .recommendation-item {
          background: white;
          border:
            1px solid #e7e7ee;
          border-radius: 18px;
          padding: 22px;
        }

        .recommendation-item-top {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .recommendation-item-top span {
          font-size: 24px;
        }

        .recommendation-item-top strong {
          color: #6840eb;
          font-size: 12px;
        }

        .recommendation-item h3 {
          margin: 18px 0 10px;
          font-size: 18px;
        }

        .recommendation-item p {
          color: #777783;
          font-size: 13px;
        }

        .similarity {
          margin-top: 15px;
          padding: 10px;
          border-radius: 10px;
          background: #f2efff;
          color: #6339df;
          font-size: 12px;
          font-weight: 700;
        }

        .recommendation-error {
          color: #d64545;
          background: #fff4f4;
          padding: 15px;
          border-radius: 12px;
          margin-top: 20px;
        }

        /* ANALYTICS */

        .analytics-section {
          margin-top: 45px;
          padding: 35px;
          background: white;
          border:
            1px solid #e7e7ee;
          border-radius: 22px;
          scroll-margin-top: 100px;
        }

        .analytics-section h2 {
          margin: 8px 0;
          font-size: 30px;
        }

        .analytics-description {
          color: #777783;
          margin-bottom: 25px;
        }

        .analytics-grid {
          display: grid;
          grid-template-columns:
            repeat(4, 1fr);
          gap: 16px;
        }

        .analytics-card {
          background: #f5f2ff;
          padding: 22px;
          border-radius: 16px;
          text-align: center;
        }

        .analytics-card strong {
          display: block;
          font-size: 30px;
          color: #6438e8;
        }

        .analytics-card span {
          display: block;
          margin-top: 7px;
          color: #777783;
          font-size: 12px;
        }

        .analytics-info {
          display: grid;
          grid-template-columns:
            repeat(3, 1fr);
          gap: 18px;
          margin-top: 25px;
        }

        .analytics-info > div {
          border:
            1px solid #eeeeF3;
          padding: 20px;
          border-radius: 15px;
        }

        .analytics-info span {
          font-size: 26px;
        }

        .analytics-info h3 {
          margin: 10px 0 6px;
          font-size: 16px;
        }

        .analytics-info p {
          margin: 0;
          color: #777783;
          font-size: 12px;
          line-height: 1.6;
        }

        /* MODAL */

        .modal-overlay {
          position: fixed;
          inset: 0;
          background:
            rgba(15,12,25,0.65);
          backdrop-filter:
            blur(8px);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 25px;
          z-index: 100;
        }

        .analysis-modal {
          width:
            min(720px, 100%);
          max-height: 90vh;
          overflow-y: auto;
          background: white;
          border-radius: 25px;
          padding: 35px;
          position: relative;
          box-shadow:
            0 30px 80px
            rgba(0,0,0,0.25);
        }

        .close-button {
          position: absolute;
          right: 20px;
          top: 18px;
          width: 35px;
          height: 35px;
          border: 0;
          border-radius: 50%;
          background: #f0eff5;
          font-size: 22px;
        }

        .modal-icon {
          width: 65px;
          height: 65px;
          border-radius: 18px;
          background: #eee9ff;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 34px;
          margin-bottom: 20px;
        }

        .analysis-modal h2 {
          font-size: 25px;
          line-height: 1.3;
          margin: 10px 0;
          padding-right: 30px;
        }

        .modal-source-link {
          display: inline-block;
          margin-bottom: 20px;
          color: #6538f5;
          font-size: 12px;
          font-weight: 700;
          text-decoration: none;
        }

        .modal-source-link:hover {
          text-decoration: underline;
        }

        /* ANALYSIS */

        .analysis-result {
          display: grid;
          grid-template-columns:
            1fr 1fr;
          gap: 15px;
        }

        .result-main,
        .result-confidence {
          background: #f7f5ff;
          border-radius: 15px;
          padding: 20px;
        }

        .result-main span,
        .result-confidence span {
          display: block;
          color: #888894;
          font-size: 11px;
          margin-bottom: 8px;
        }

        .result-main strong {
          font-size: 25px;
          color: #6438e8;
        }

        .result-confidence strong {
          font-size: 25px;
          color: #38a878;
        }

        .explanation {
          margin-top: 20px;
          padding: 20px;
          border-radius: 15px;
          background: #fafafa;
        }

        .explanation h3,
        .keywords h3 {
          font-size: 14px;
          margin-top: 0;
        }

        .explanation p {
          color: #686874;
          font-size: 13px;
          line-height: 1.7;
        }

        .keywords {
          margin-top: 20px;
        }

        .keywords > div {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .keywords span {
          padding: 8px 12px;
          border-radius: 20px;
          background: #eee9ff;
          color: #6339df;
          font-size: 11px;
          font-weight: 700;
        }

        .analysis-loading {
          padding: 35px;
          text-align: center;
          background: #f7f5ff;
          border-radius: 15px;
        }

        /* SUMMARY */

        .ai-summary {
          margin-top: 20px;
          padding: 20px;
          border-radius: 17px;
          background:
            linear-gradient(
              135deg,
              #f3efff,
              #faf9ff
            );
          border:
            1px solid #e2d9ff;
        }

        .summary-title {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 12px;
        }

        .summary-title h3 {
          margin: 0;
          color: #6037e4;
          font-size: 15px;
        }

        .summary-sparkle {
          width: 32px;
          height: 32px;
          border-radius: 10px;
          background: #6b3cff;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .ai-summary p {
          margin: 0;
          color: #5f5f6c;
          font-size: 13px;
          line-height: 1.8;
        }

        .loading-bar {
          width: 100%;
          height: 5px;
          background: #e8e2ff;
          border-radius: 10px;
          overflow: hidden;
        }

        .loading-bar span {
          display: block;
          width: 45%;
          height: 100%;
          background: #683aff;
          animation:
            loadingAnimation
            1.2s infinite;
        }

        .summary-error {
          background: #fff4f4;
          border-color: #ffd6d6;
        }

        /* TRANSLATION */

        .translation-panel {
          margin-top: 20px;
          padding: 20px;
          border-radius: 18px;
          background:
            linear-gradient(
              135deg,
              #eef8ff,
              #f8fbff
            );
          border:
            1px solid #d6eaff;
        }

        .translation-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 18px;
        }

        .translation-header > div {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .translation-icon {
          width: 40px;
          height: 40px;
          border-radius: 12px;
          background: #3478f6;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .translation-header h3 {
          margin: 0;
          color: #2461c5;
          font-size: 15px;
        }

        .translation-header p {
          margin: 4px 0 0;
          color: #7b8797;
          font-size: 11px;
        }

        .translation-close {
          width: 30px;
          height: 30px;
          border: 0;
          border-radius: 50%;
          background: #e5f1ff;
          color: #3972bd;
          font-size: 18px;
        }

        .translation-controls {
          display: grid;
          grid-template-columns:
            auto 1fr auto;
          align-items: center;
          gap: 12px;
        }

        .translation-controls label {
          font-size: 12px;
          font-weight: 700;
          color: #66778a;
        }

        .translation-controls select {
          border:
            1px solid #cbdff5;
          background: white;
          padding: 11px 13px;
          border-radius: 10px;
          outline: none;
        }

        .do-translate-button {
          border: 0;
          background: #3478f6;
          color: white;
          padding: 11px 16px;
          border-radius: 10px;
          font-weight: 700;
          white-space: nowrap;
        }

        .translation-loading,
        .translation-result,
        .translation-error {
          margin-top: 18px;
          padding: 18px;
          border-radius: 14px;
          background: white;
        }

        .translation-loading {
          text-align: center;
          border:
            1px solid #dcecff;
        }

        .translation-spinner {
          font-size: 28px;
          color: #3478f6;
          animation:
            spin 1s linear infinite;
        }

        .translation-result {
          border:
            1px solid #d6eaff;
        }

        .translation-result-title {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 10px;
        }

        .translation-result-title span {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: #38a878;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .translation-result p {
          margin: 0;
          color: #4f6072;
          line-height: 1.8;
        }

        .translation-error {
          background: #fff4f4;
          border:
            1px solid #ffd6d6;
        }

        .translation-error strong {
          color: #d64545;
        }

        /* BUTTONS */

        .modal-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          margin-top: 25px;
        }

        .modal-actions button,
        .original-button {
          border: 0;
          color: white;
          padding: 11px 15px;
          border-radius: 10px;
          font-size: 12px;
          font-weight: 700;
          text-decoration: none;
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }

        .summary-button {
          background: #673bfa;
        }

        .translate-button {
          background: #3478f6;
        }

        .original-button {
          background: #159267;
        }

        .recommend-button {
          background: #e84375;
        }

        /* ANIMATIONS */

        @keyframes spin {
          from {
            transform:
              rotate(0deg);
          }

          to {
            transform:
              rotate(360deg);
          }
        }

        @keyframes loadingAnimation {
          0% {
            transform:
              translateX(-100%);
          }

          100% {
            transform:
              translateX(250%);
          }
        }

        /* TABLET */

        @media (max-width: 950px) {

          nav {
            gap: 12px;
          }

          .nav-link {
            font-size: 12px;
          }

          .hero {
            grid-template-columns:
              1fr;
          }

          .news-grid {
            grid-template-columns:
              repeat(2, 1fr);
          }

          .analytics-grid {
            grid-template-columns:
              repeat(2, 1fr);
          }

        }

        /* MOBILE */

        @media (max-width: 650px) {

          nav {
            display: none;
          }

          .navbar {
            padding:
              0 18px;
          }

          .hero {
            padding:
              45px 18px;
          }

          .hero h2 {
            font-size: 46px;
          }

          .content {
            padding-left: 18px;
            padding-right: 18px;
          }

          .news-grid,
          .bottom-section,
          .recommendations-grid,
          .analytics-grid,
          .analytics-info {
            grid-template-columns:
              1fr;
          }

          .section-header {
            align-items:
              flex-start;
            flex-direction:
              column;
            gap: 15px;
          }

          .search-box {
            height: auto;
            padding: 10px;
          }

          .analysis-modal {
            padding: 25px;
          }

          .analysis-result {
            grid-template-columns:
              1fr;
          }

          .translation-controls {
            grid-template-columns:
              1fr;
          }

          .modal-actions {
            flex-direction:
              column;
          }

          .modal-actions button,
          .original-button {
            width: 100%;
          }

        }

      `}</style>

    </div>
  );
}

export default News;