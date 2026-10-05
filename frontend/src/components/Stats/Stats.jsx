const stats = [
  {
    title: "Articles",
    value: "10K+",
  },
  {
    title: "Languages",
    value: "5",
  },
  {
    title: "Classification Accuracy",
    value: "97%",
  },
  {
    title: "Active Users",
    value: "500+",
  },
];

function Stats() {
  return (
    <section className="max-w-7xl mx-auto py-16 px-8">

      <h2 className="text-4xl font-bold text-center mb-12">
        Platform Statistics
      </h2>

      <div className="grid md:grid-cols-4 gap-8">

        {stats.map((item, index) => (

          <div
            key={index}
            className="bg-slate-900 rounded-2xl p-8 text-center hover:scale-105 transition shadow-xl"
          >

            <h1 className="text-5xl font-bold text-cyan-400">
              {item.value}
            </h1>

            <p className="mt-4 text-slate-400">
              {item.title}
            </p>

          </div>

        ))}

      </div>

    </section>
  );
}

export default Stats;