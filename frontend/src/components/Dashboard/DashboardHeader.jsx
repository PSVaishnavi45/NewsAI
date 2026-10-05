import { useAuth } from "../../context/AuthContext";

function DashboardHeader() {
  const { user } = useAuth();

  return (
    <header className="flex justify-between items-center mb-8">
      <div>
        <h2 className="text-4xl font-bold">
          Welcome, {user?.name || "Guest"} 👋
        </h2>

        <p className="text-slate-500 mt-2">
          Explainable AI News Dashboard
        </p>
      </div>

      <button className="bg-cyan-500 px-5 py-3 rounded-xl hover:bg-cyan-400">
        Upload News
      </button>
    </header>
  );
}

export default DashboardHeader;