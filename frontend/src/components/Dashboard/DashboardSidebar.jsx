import { Link } from "react-router-dom";

function DashboardSidebar() {
  const menuItems = [
    "Dashboard",
    "News Classification",
    "Recommendations",
    "Semantic Search",
    "Summarization",
    "Translation",
    "Analytics",
    "Profile",
  ];

  return (
    <aside className="w-72 bg-slate-900 text-white min-h-screen p-6">
      <h1 className="text-3xl font-bold text-cyan-400 mb-10">
        📰 NewsAI
      </h1>

      <nav className="space-y-4">
        {menuItems.map((item) => (
          <Link
            key={item}
            to="#"
            className="block p-3 rounded-xl hover:bg-cyan-500 transition"
          >
            {item}
          </Link>
        ))}
      </nav>
    </aside>
  );
}

export default DashboardSidebar;