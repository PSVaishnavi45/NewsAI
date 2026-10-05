import Navbar from "../components/Navbar/Navbar";
import Hero from "../components/Hero/Hero";
import NewsCard from "../components/NewsCard/NewsCard";
import Stats from "../components/Stats/Stats";
import Features from "../components/Features/Features";
import newsData from "../data/newsData";
function Home() {

  const news = [

    {
      title: "AI Revolutionizes Healthcare",
      category: "Technology",
      summary:
        "Artificial Intelligence is transforming healthcare through faster diagnosis and personalized treatment.",

      image:
        "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=900",
    },

    {
      title: "India Launches New Space Mission",
      category: "Science",

      summary:
        "ISRO successfully launches its latest satellite mission to improve climate monitoring.",

      image:
        "https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=900",
    },

    {
      title: "Global Markets Show Strong Growth",
      category: "Business",

      summary:
        "International stock markets witness positive growth driven by AI investments.",

      image:
        "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?w=900",
    },

  ];

  return (

    <div className="min-h-screen bg-slate-950 text-white">

      <Navbar />

      <Hero />

      <Stats />

      <Features />

      <section className="max-w-7xl mx-auto px-8 py-20">

        <h2 className="text-4xl font-bold mb-10">

          🔥 Featured News

        </h2>

        <div className="grid md:grid-cols-3 gap-8">

          {newsData.map((item) => (
  <NewsCard key={item.id} {...item} />
))}

        </div>

      </section>

    </div>

  );
}

export default Home;