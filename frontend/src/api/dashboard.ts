import api from "./client";
import type { DashboardKPIs, RecentActivity, StockAlertItem } from "@/types/dashboard";

export const dashboardApi = {
  kpis: () => api.get<DashboardKPIs>("/dashboard/kpis").then((r) => r.data),
  activity: (limit = 10) => api.get<RecentActivity[]>("/dashboard/activity", { params: { limit } }).then((r) => r.data),
  alerts: () => api.get<StockAlertItem[]>("/dashboard/alerts").then((r) => r.data),
};
