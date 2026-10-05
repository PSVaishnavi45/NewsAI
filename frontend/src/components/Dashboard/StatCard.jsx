function StatCard({ title, value }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-8">

      <h3 className="text-slate-500">
        {title}
      </h3>

      <h1 className="text-5xl font-bold mt-5">
        {value}
      </h1>

    </div>
  );
}

export default StatCard;