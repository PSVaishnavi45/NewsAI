import { useEffect, useState } from "react";
import DashboardSidebar from "../components/Dashboard/DashboardSidebar";
import DashboardHeader from "../components/Dashboard/DashboardHeader";
import StatCard from "../components/Dashboard/StatCard";
import { getDashboardStats } from "../api/dashboardApi";

function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      const data = await getDashboardStats();
      setStats(data);
    };

    fetchStats();
  }, []);

  if (!stats) {
    return (
      <div className="flex justify-center items-center min-h-screen text-2xl">
        Loading...
      </div>
    );
  }

  return (
    <div className="flex bg-slate-100 min-h-screen">
      <DashboardSidebar />

      <main className="flex-1 p-10">
        <DashboardHeader />

        <div className="grid md:grid-cols-4 gap-6">
          <StatCard title="Articles" value={stats.articles} />
          <StatCard title="Languages" value={stats.languages} />
          <StatCard title="Accuracy" value={`${stats.accuracy}%`} />
          <StatCard title="Users" value={stats.users} />
        </div>
      </main>
    </div>
  );
}

export default Dashboard;