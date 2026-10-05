function NewsCard({ title, category, summary, image, confidence, language }) {
  return (
    <div className="bg-slate-900 rounded-2xl overflow-hidden shadow-xl hover:scale-105 transition duration-300">

      <img
        src={image}
        alt={title}
        className="w-full h-56 object-cover"
      />

      <div className="p-6">

        <div className="flex justify-between mb-4">

          <span className="bg-cyan-500 px-3 py-1 rounded-full text-sm">
            {category}
          </span>

          <span className="bg-green-600 px-3 py-1 rounded-full text-sm">
            {confidence}%
          </span>

        </div>

        <h2 className="text-2xl font-bold">
          {title}
        </h2>

        <p className="text-slate-400 mt-4">
          {summary}
        </p>

        <div className="flex justify-between items-center mt-6">

          <span className="text-cyan-400">
            🌍 {language}
          </span>

          <button className="bg-cyan-500 px-4 py-2 rounded-lg hover:bg-cyan-400">
            Read More
          </button>

        </div>

      </div>
    </div>
  );
}

export default NewsCard;