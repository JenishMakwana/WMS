import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { productApi, locationApi } from "@/api/inventory";
import api from "@/api/client";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { formatNumber } from "@/utils/format";
import type { ProductListItem } from "@/types/inventory";
import type { Location } from "@/types/inventory";

interface AdjLine {
  product_id: string;
  location_id: string;
  counted_qty: string;
  note: string;
  product?: ProductListItem;
  location?: Location;
}

export default function AdjustmentsPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [lines, setLines] = useState<AdjLine[]>([
    { product_id: "", location_id: "", counted_qty: "", note: "" },
  ]);
  const [globalNote, setGlobalNote] = useState("");

  const { data: products = [] } = useQuery({ queryKey: ["products"], queryFn: () => productApi.list() });
  const { data: locations = [] } = useQuery({ queryKey: ["locations"], queryFn: () => locationApi.list() });

  const submitMutation = useMutation({
    mutationFn: () =>
      api.post("/adjustments/", {
        notes: globalNote || undefined,
        lines: lines
          .filter((l) => l.product_id && l.location_id && l.counted_qty !== "")
          .map((l) => ({
            product_id: l.product_id,
            location_id: l.location_id,
            counted_qty: l.counted_qty,
            note: l.note || undefined,
          })),
      }).then((r) => r.data),
    onSuccess: (data: { id: string }) => {
      qc.invalidateQueries({ queryKey: ["products"] });
      qc.invalidateQueries({ queryKey: ["dashboard-kpis"] });
      navigate(`/operations/${data.id}`);
    },
  });

  const updateLine = (i: number, field: keyof AdjLine, value: string) => {
    setLines((prev) => prev.map((l, idx) => idx === i ? { ...l, [field]: value } : l));
  };

  const addLine = () => setLines((l) => [...l, { product_id: "", location_id: "", counted_qty: "", note: "" }]);
  const removeLine = (i: number) => setLines((l) => l.filter((_, idx) => idx !== i));

  const validLines = lines.filter((l) => l.product_id && l.location_id && l.counted_qty !== "");

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="Stock adjustment"
        subtitle="Reconcile physical counts with recorded stock"
        action={
          <div className="flex gap-2">
            <Button variant="ghost" className="w-auto px-3" onClick={() => navigate(-1)}>Cancel</Button>
            <Button
              className="w-auto px-4"
              onClick={() => submitMutation.mutate()}
              loading={submitMutation.isPending}
              disabled={validLines.length === 0}
            >
              Apply adjustment
            </Button>
          </div>
        }
      />

      <div className="flex-1 overflow-auto p-6 space-y-6">

        {/* Info banner */}
        <div className="rounded-xl border border-brand-600/20 bg-brand-600/5 px-5 py-4">
          <p className="text-sm text-brand-400">
            Enter the physically counted quantity for each product. The system will calculate the difference and update stock automatically.
          </p>
        </div>

        {/* Global note */}
        <div className="flex flex-col gap-1.5 max-w-md">
          <label className="text-sm font-medium text-gray-300">Adjustment note (optional)</label>
          <input
            className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3.5 py-2.5 text-sm text-gray-100 placeholder:text-gray-500 outline-none focus:border-brand-400"
            placeholder="e.g. Monthly physical count — March 2026"
            value={globalNote}
            onChange={(e) => setGlobalNote(e.target.value)}
          />
        </div>

        {/* Lines table */}
        <div className="rounded-xl border border-gray-800 bg-gray-900">
          <div className="flex items-center justify-between border-b border-gray-800 px-5 py-4">
            <h3 className="text-sm font-medium text-gray-100">Products to adjust</h3>
            <button onClick={addLine} className="text-xs text-brand-400 hover:text-brand-100 transition-colors">+ Add product</button>
          </div>

          <div className="divide-y divide-gray-800/60">
            {lines.map((line, i) => {
              const product = products.find((p) => p.id === line.product_id);

              return (
                <div key={i} className="px-5 py-4">
                  <div className="grid grid-cols-12 gap-3 items-end">
                    {/* Product */}
                    <div className="col-span-4 flex flex-col gap-1.5">
                      {i === 0 && <label className="text-xs text-gray-500">Product</label>}
                      <select
                        className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2.5 text-sm text-gray-100 outline-none focus:border-brand-400"
                        value={line.product_id}
                        onChange={(e) => updateLine(i, "product_id", e.target.value)}
                      >
                        <option value="">— Select product —</option>
                        {products.map((p) => (
                          <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
                        ))}
                      </select>
                    </div>

                    {/* Location */}
                    <div className="col-span-3 flex flex-col gap-1.5">
                      {i === 0 && <label className="text-xs text-gray-500">Location</label>}
                      <select
                        className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2.5 text-sm text-gray-100 outline-none focus:border-brand-400"
                        value={line.location_id}
                        onChange={(e) => updateLine(i, "location_id", e.target.value)}
                      >
                        <option value="">— Select location —</option>
                        {locations.map((l) => (
                          <option key={l.id} value={l.id}>{l.warehouse_name} / {l.name}</option>
                        ))}
                      </select>
                    </div>

                    {/* Current stock (read-only info) */}
                    <div className="col-span-1 flex flex-col gap-1.5">
                      {i === 0 && <label className="text-xs text-gray-500">Current</label>}
                      <div className="rounded-lg border border-gray-800 bg-gray-800/50 px-3 py-2.5 text-sm text-gray-400 tabular-nums">
                        {product ? formatNumber(product.total_stock) : "—"}
                      </div>
                    </div>

                    {/* Counted qty */}
                    <div className="col-span-2 flex flex-col gap-1.5">
                      {i === 0 && <label className="text-xs text-gray-500">Counted qty</label>}
                      <input
                        type="number"
                        min="0"
                        step="0.001"
                        placeholder="0"
                        className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2.5 text-sm text-gray-100 placeholder:text-gray-500 outline-none focus:border-brand-400"
                        value={line.counted_qty}
                        onChange={(e) => updateLine(i, "counted_qty", e.target.value)}
                      />
                    </div>

                    {/* Delta preview */}
                    <div className="col-span-1 flex flex-col gap-1.5">
                      {i === 0 && <label className="text-xs text-gray-500">Delta</label>}
                      <div className={`rounded-lg border border-gray-800 bg-gray-800/50 px-3 py-2.5 text-sm font-medium tabular-nums ${
                        !product || line.counted_qty === "" ? "text-gray-600" :
                        parseFloat(line.counted_qty) - parseFloat(product.total_stock) > 0 ? "text-green-400" :
                        parseFloat(line.counted_qty) - parseFloat(product.total_stock) < 0 ? "text-red-400" :
                        "text-gray-500"
                      }`}>
                        {product && line.counted_qty !== ""
                          ? (() => {
                              const d = parseFloat(line.counted_qty) - parseFloat(product.total_stock);
                              return d > 0 ? `+${formatNumber(d)}` : formatNumber(d);
                            })()
                          : "—"}
                      </div>
                    </div>

                    {/* Remove */}
                    <div className="col-span-1 flex items-end justify-end pb-0.5">
                      {lines.length > 1 && (
                        <button onClick={() => removeLine(i)} className="text-red-400 hover:text-red-300 transition-colors">
                          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Optional line note */}
                  {line.product_id && (
                    <div className="mt-2 max-w-md">
                      <input
                        className="w-full rounded-lg border border-gray-800 bg-transparent px-3 py-1.5 text-xs text-gray-500 placeholder:text-gray-700 outline-none focus:border-gray-600"
                        placeholder="Line note (optional)"
                        value={line.note}
                        onChange={(e) => updateLine(i, "note", e.target.value)}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="border-t border-gray-800 px-5 py-3">
            <p className="text-xs text-gray-600">
              {validLines.length} of {lines.length} line{lines.length !== 1 ? "s" : ""} ready to submit
            </p>
          </div>
        </div>

        {submitMutation.isError && (
          <div className="rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4">
            <p className="text-sm text-red-400">Failed to apply adjustment. Please check your inputs.</p>
          </div>
        )}
      </div>
    </div>
  );
}
