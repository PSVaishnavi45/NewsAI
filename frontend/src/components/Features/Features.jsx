const features = [

  "Explainable AI",

  "Multilingual News",

  "Cross Language Recommendation",

  "Semantic Search",

  "AI Summarization",

  "Translation",

];

function Features() {

  return (

    <section className="max-w-7xl mx-auto py-20 px-8">

      <h2 className="text-4xl font-bold text-center mb-10">

        AI Features

      </h2>

      <div className="grid md:grid-cols-3 gap-8">

        {features.map((item, index) => (

          <div

            key={index}

            className="bg-slate-900 rounded-2xl p-10 hover:bg-cyan-500 hover:text-black transition"

          >

            <h3 className="text-2xl font-semibold">

              {item}

            </h3>

          </div>

        ))}

      </div>

    </section>

  );

}

export default Features;