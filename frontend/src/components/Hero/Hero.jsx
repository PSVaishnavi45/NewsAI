function Hero() {
  return (
    <section className="text-center py-24 px-6">

      <p className="text-cyan-400 uppercase tracking-widest">
        AI Powered Platform
      </p>

      <h1 className="text-6xl font-extrabold mt-5 leading-tight">
        Explainable <span className="text-cyan-400">Multilingual</span>
        <br />
        News Intelligence
      </h1>

      <p className="text-slate-400 mt-8 text-xl max-w-3xl mx-auto">
        Discover trustworthy news using Transformer-based NLP,
        Explainable AI, Semantic Search, Personalized
        Recommendation and Multilingual Support.
      </p>

      <div className="mt-12 flex justify-center gap-4 flex-wrap">

        <input
          type="text"
          placeholder="Search News..."
          className="w-[450px] max-w-full p-4 rounded-xl text-black"
        />

        <button className="bg-cyan-500 px-8 rounded-xl hover:bg-cyan-400 transition">
          Search
        </button>

      </div>

    </section>
  );
}

export default Hero;