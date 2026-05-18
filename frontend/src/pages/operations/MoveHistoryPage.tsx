import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { operationApi } from "@/api/operations";
import { productApi } from "@/api/inventory";
import { PageHeader } from "@/components/ui/PageHeader";
import { TypeBadge } from "@/components/operations/StatusBadge";
import { formatNumber, formatDate } from "@/utils/format";
import type { OperationType } from "@/types/operations";

export default function MoveHistoryPage() {
  const [productFilter, setProductFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState<OperationType | "">("");

  const { data: products = [] } = useQuery({ queryKey: ["products"], queryFn: () => productApi.list() });

  const { data: ledger = [], isLoading } = useQuery({
    queryKey: ["ledger", productFilter, typeFilter],
    queryFn: () => operationApi.ledger({
      product_id: productFilter || undefined,
      type: (typeFilter as OperationType) || undefined,
      limit: 200,
    }),
  });

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Move history" subtitle="Full audit trail of every stock movement" />

      {/* Filters */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-800">
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500">Product</label>
          <select
            className="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-100 outline-none focus:border-brand-400 min-w-[200px]"
            value={productFilter}
            onChange={(e) => setProductFilter(e.target.value)}
          >
            <option value="">All products</option>
            {products.map((p) => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500">Operation type</label>
          <select
            className="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-100 outline-none focus:border-brand-400"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as OperationType | "")}
          >
            <option value="">All types</option>
            <option value="RECEIPT">Receipt</option>
            <option value="DELIVERY">Delivery</option>
            <option value="INTERNAL">Transfer</option>
            <option value="ADJUSTMENT">Adjustment</option>
          </select>
        </div>
        <div className="ml-auto text-xs text-gray-500">
          {ledger.length} entries
        </div>
      </div>

      {/* Ledger table */}
      <div className="flex-1 overflow-auto px-6 py-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-20 text-gray-500 text-sm">Loading…</div>
        ) : ledger.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <p className="text-gray-500 text-sm">No movements recorded yet.</p>
            <p className="mt-1 text-xs text-gray-600">Validate a receipt or delivery to see entries here.</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-left text-xs text-gray-500 uppercase tracking-wide">
                <th className="pb-3 font-medium">Date</th>
                <th className="pb-3 font-medium">Reference</th>
                <th className="pb-3 font-medium">Type</th>
                <th className="pb-3 font-medium">Product</th>
                <th className="pb-3 font-medium">Location</th>
                <th className="pb-3 font-medium text-right">Change</th>
                <th className="pb-3 font-medium text-right">Balance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {ledger.map((e) => (
                <tr key={e.id} className="hover:bg-gray-800/40 transition-colors">
                  <td className="py-3 pr-4 text-gray-400 whitespace-nowrap">
                    {formatDate(e.created_at)}
                  </td>
                  <td className="py-3 pr-4 font-mono text-brand-400 text-xs">
                    {e.operation_reference ?? "—"}
                  </td>
                  <td className="py-3 pr-4">
                    {e.operation_type ? <TypeBadge type={e.operation_type} /> : "—"}
                  </td>
                  <td className="py-3 pr-4">
                    <p className="font-medium text-gray-100">{e.product_name}</p>
                    <p className="text-xs text-gray-500 font-mono">{e.product_sku}</p>
                  </td>
                  <td className="py-3 pr-4 text-gray-400">
                    <p>{e.location_name}</p>
                    <p className="text-xs text-gray-600">{e.warehouse_name}</p>
                  </td>
                  <td className={`py-3 pr-4 text-right font-medium tabular-nums ${parseFloat(e.qty_change) >= 0 ? "text-green-400" : "text-red-400"}`}>
                    {parseFloat(e.qty_change) >= 0 ? "+" : ""}{formatNumber(e.qty_change)}
                  </td>
                  <td className="py-3 text-right font-medium text-gray-100 tabular-nums">
                    {formatNumber(e.balance_after)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
