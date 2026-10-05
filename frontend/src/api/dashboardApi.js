import api from "./api";

export const getDashboardStats = async () => {
  const response = await api.get("/api/stats");
  return response.data;
};