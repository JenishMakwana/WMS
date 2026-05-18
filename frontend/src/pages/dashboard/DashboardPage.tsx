import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { dashboardApi } from "@/api/dashboard";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { PageHeader } from "@/components/ui/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { StatusBadge, TypeBadge } from "@/components/operations/StatusBadge";
import { useAlerts } from "@/hooks/useAlerts";
import { useToasts, ToastContainer } from "@/components/ui/Toast";
import { formatNumber, formatDate } from "@/utils/format";


export default function DashboardPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { toasts, push, dismiss } = useToasts();

  // Subscribe to real-time alerts
  useAlerts((msg) => {
    push(msg);
    qc.invalidateQueries({ queryKey: ["dashboard-alerts"] });
    qc.invalidateQueries({ queryKey: ["dashboard-kpis"] });
  });

  const { data: kpis, isLoading: kpisLoading } = useQuery({
    queryKey: ["dashboard-kpis"],
    queryFn: dashboardApi.kpis,
    refetchInterval: 30_000, // refresh every 30s as fallback
  });

  const { data: activity = [] } = useQuery({
    queryKey: ["dashboard-activity"],
    queryFn: () => dashboardApi.activity(8),
    refetchInterval: 30_000,
  });

  const { data: alerts = [] } = useQuery({
    queryKey: ["dashboard-alerts"],
    queryFn: dashboardApi.alerts,
  });

  return (
    <div className="flex flex-col h-full overflow-auto">
      <PageHeader
        title="Dashboard"
        subtitle={`Inventory overview · ${formatDate(new Date().toISOString())}`}
      />

      <div className="flex-1 p-6 space-y-6">

        {/* KPI grid */}
        {kpisLoading ? (
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-24 rounded-xl border border-gray-800 bg-gray-900 animate-pulse" />
            ))}
          </div>
        ) : kpis && (
          <>
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              <KpiCard label="Total products" value={kpis.total_products} sub="active SKUs" />
              <KpiCard label="Total stock" value={formatNumber(kpis.total_stock_value)} sub="units across all locations" />
              <KpiCard
                label="Out of stock"
                value={kpis.out_of_stock_count}
                sub="zero units remaining"
                variant={kpis.out_of_stock_count > 0 ? "danger" : "default"}
              />
            </div>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              <KpiCard
                label="Pending receipts"
                value={kpis.pending_receipts}
                sub="draft + confirmed"
                variant={kpis.pending_receipts > 0 ? "warning" : "default"}
                onClick={() => navigate("/receipts")}
              />
              <KpiCard
                label="Pending deliveries"
                value={kpis.pending_deliveries}
                sub="draft + confirmed"
                variant={kpis.pending_deliveries > 0 ? "warning" : "default"}
                onClick={() => navigate("/deliveries")}
              />
              <KpiCard label="Transfers scheduled" value={kpis.internal_transfers_scheduled} sub="internal moves pending" />
            </div>
            <div className="rounded-xl border border-gray-800 bg-gray-900 px-5 py-4">
              <p className="text-xs text-gray-500 mb-1">Today's activity</p>
              <p className="text-sm font-medium text-gray-100">{kpis.receipts_today + kpis.deliveries_today} operations</p>
              <p className="text-xs text-gray-500 mt-1">{kpis.receipts_today} receipts · {kpis.deliveries_today} deliveries</p>
            </div>
          </>
        )}

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">

          {/* Stock alerts */}
          <div className="rounded-xl border border-gray-800 bg-gray-900">
            <div className="flex items-center justify-between border-b border-gray-800 px-5 py-4">
              <h3 className="text-sm font-medium text-gray-100">Stock alerts</h3>
              {alerts.length > 0 && (
                <span className="rounded-full bg-red-500/10 border border-red-500/20 px-2 py-0.5 text-xs text-red-400">
                  {alerts.length} item{alerts.length !== 1 ? "s" : ""}
                </span>
              )}
            </div>
            {alerts.length === 0 ? (
              <div className="px-5 py-8 text-center">
                <p className="text-sm text-gray-500">All stock levels are healthy.</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-800/60">
                {alerts.slice(0, 6).map((a) => (
                  <div key={a.product_id} className="flex items-center justify-between px-5 py-3">
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-100 truncate">{a.product_name}</p>
                      <p className="text-xs font-mono text-gray-500">{a.sku}</p>
                    </div>
                    <div className="flex items-center gap-3 ml-3 shrink-0">
                      <span className="text-sm font-medium tabular-nums text-gray-300">
                        {formatNumber(a.total_stock)} {a.unit_of_measure}
                      </span>
                      <Badge variant="danger">Out of stock</Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent activity */}
          <div className="rounded-xl border border-gray-800 bg-gray-900">
            <div className="flex items-center justify-between border-b border-gray-800 px-5 py-4">
              <h3 className="text-sm font-medium text-gray-100">Recent activity</h3>
              <button onClick={() => navigate("/history")} className="text-xs text-brand-400 hover:text-brand-100 transition-colors">
                View ledger →
              </button>
            </div>
            {activity.length === 0 ? (
              <div className="px-5 py-8 text-center">
                <p className="text-sm text-gray-500">No operations yet.</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-800/60">
                {activity.map((a) => (
                  <div
                    key={a.operation_id}
                    className="flex items-center justify-between px-5 py-3 cursor-pointer hover:bg-gray-800/30 transition-colors"
                    onClick={() => navigate(`/operations/${a.operation_id}`)}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <TypeBadge type={a.type} />
                      <div className="min-w-0">
                        <p className="text-sm font-mono text-gray-200">{a.reference}</p>
                        <p className="text-xs text-gray-500 truncate">{a.party ?? "—"} · {a.move_count} line{a.move_count !== 1 ? "s" : ""}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 ml-3 shrink-0">
                      <StatusBadge status={a.status} />
                      <span className="text-xs text-gray-600">
                        {formatDate(a.created_at)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Real-time toast notifications */}
      <ToastContainer toasts={toasts} dismiss={dismiss} />
    </div>
  );
}
