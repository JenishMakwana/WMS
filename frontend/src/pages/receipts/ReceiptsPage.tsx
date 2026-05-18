import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm, useFieldArray } from "react-hook-form";
import { Link } from "react-router-dom";
import { operationApi } from "@/api/operations";
import { productApi, locationApi } from "@/api/inventory";
import { supplierApi } from "@/api/parties";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { StatusBadge } from "@/components/operations/StatusBadge";
import { formatDate } from "@/utils/format";

import { useToasts, ToastContainer } from "@/components/ui/Toast";

export default function ReceiptsPage() {
  const qc = useQueryClient();
  const { alert, toasts, dismiss } = useToasts();
  const [showModal, setShowModal] = useState(false);
  const [printingId, setPrintingId] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewRef, setPreviewRef] = useState<string>("");

  useEffect(() => {
    return () => { if (previewUrl) window.URL.revokeObjectURL(previewUrl); };
  }, [previewUrl]);

  const { data: receipts = [], isLoading, isFetching } = useQuery({
    queryKey: ["operations", "RECEIPT"],
    queryFn: () => operationApi.list({ type: "RECEIPT" }),
    staleTime: 60_000,
  });

  const handlePreview = async (id: string, ref: string) => {
    setPrintingId(id);
    setPreviewRef(ref);
    try {
      const blob = await operationApi.getPdfBlob(id);
      const url = window.URL.createObjectURL(blob);
      setPreviewUrl(url);
    } catch (err) {
      console.error("Failed to generate preview", err);
      alert("Error", "Could not generate PDF preview.", "error");
    } finally {
      setPrintingId(null);
    }
  };

  const { data: products = [] } = useQuery({ queryKey: ["products"], queryFn: () => productApi.list(), enabled: showModal });
  const { data: locations = [] } = useQuery({ queryKey: ["locations"], queryFn: () => locationApi.list(), enabled: showModal });
  const { data: suppliers = [] } = useQuery({ queryKey: ["suppliers"], queryFn: () => supplierApi.list(), enabled: showModal });

  const { register, control, handleSubmit, reset } = useForm({
    defaultValues: { supplier_id: "", dest_location_id: "", scheduled_date: "", moves: [{ product_id: "", demand_qty: "" }] },
  });
  const { fields, append, remove } = useFieldArray({ control, name: "moves" });

  const buildReceiptPayload = (data: any) => {
    const selectedSupplier = suppliers.find((s) => s.id === data.supplier_id);
    return {
      type: "RECEIPT" as const,
      supplier: selectedSupplier?.name || undefined,
      supplier_id: data.supplier_id || undefined,
      dest_location_id: data.dest_location_id || undefined,
      scheduled_date: data.scheduled_date ? `${data.scheduled_date}T00:00:00` : undefined,
      moves: (data.moves ?? [])
        .filter((move: any) => move.product_id && move.demand_qty)
        .map((move: any) => ({
          product_id: move.product_id,
          demand_qty: move.demand_qty,
        })),
    };
  };

  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => operationApi.create(data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["operations"] }); setShowModal(false); reset(); },
  });

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="Receipts"
        subtitle="Incoming goods from suppliers"
        action={
          <div className="flex items-center gap-3">
            {isFetching && !isLoading && <span className="text-xs text-gray-500">Refreshing...</span>}
            <Button className="w-auto px-4" onClick={() => setShowModal(true)}>+ New receipt</Button>
          </div>
        }
      />

      <div className="flex-1 overflow-auto px-6 py-4">
        {isLoading ? (
          <div className="rounded-xl border border-gray-800 bg-gray-900 overflow-hidden animate-pulse">
            <div className="grid grid-cols-7 gap-4 border-b border-gray-800 px-4 py-3">
              {Array.from({ length: 7 }).map((_, index) => (
                <div key={index} className="h-3 rounded bg-gray-800" />
              ))}
            </div>
            {Array.from({ length: 6 }).map((_, rowIndex) => (
              <div key={rowIndex} className="grid grid-cols-7 gap-4 border-b border-gray-800/60 px-4 py-4 last:border-b-0">
                {Array.from({ length: 7 }).map((_, colIndex) => (
                  <div
                    key={`${rowIndex}-${colIndex}`}
                    className={colIndex === 6 ? "h-3 w-6 justify-self-end rounded bg-gray-800" : "h-3 rounded bg-gray-800"}
                  />
                ))}
              </div>
            ))}
          </div>
        ) : receipts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <p className="text-gray-500 text-sm">No receipts yet.</p>
            <button onClick={() => setShowModal(true)} className="mt-3 text-sm text-brand-400 hover:text-brand-100">Create your first receipt</button>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-left text-xs text-gray-500 uppercase tracking-wide">
                <th className="pb-3 font-medium">Reference</th>
                <th className="pb-3 font-medium">Supplier</th>
                <th className="pb-3 font-medium">Destination</th>
                <th className="pb-3 font-medium">Lines</th>
                <th className="pb-3 font-medium">Date</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium text-right pr-4">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {receipts.map((r) => (
                <tr key={r.id} className="hover:bg-gray-800/40 transition-colors">
                  <td className="py-3 pr-4">
                    <Link to={`/operations/${r.id}`} className="font-mono text-brand-400 hover:text-brand-100 transition-colors">{r.reference}</Link>
                  </td>
                  <td className="py-3 pr-4 text-gray-300">{r.supplier_name || r.supplier || "—"}</td>
                  <td className="py-3 pr-4 text-gray-400">{r.dest_location_name ?? "—"}</td>
                  <td className="py-3 pr-4 text-gray-400">{r.move_count}</td>
                  <td className="py-3 pr-4 text-gray-400">{formatDate(r.scheduled_date ?? r.created_at)}</td>
                  <td className="py-3"><StatusBadge status={r.status} /></td>
                  <td className="py-3 text-right pr-4">
                    <button
                      onClick={() => handlePreview(r.id, r.reference)}
                      disabled={printingId === r.id}
                      className="text-brand-400 hover:text-brand-100 disabled:opacity-50"
                      title="Preview Invoice"
                    >
                      {printingId === r.id ? (
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                      ) : (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      )}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal
        open={!!previewUrl}
        onClose={() => setPreviewUrl(null)}
        title={`Preview: ${previewRef}`}
        width="max-w-4xl"
      >
        <div className="h-[70vh] w-full">
          {previewUrl && (
            <iframe
              src={previewUrl}
              className="h-full w-full rounded-lg border border-gray-800"
              title="PDF Preview"
            />
          )}
        </div>
        <div className="flex justify-end mt-4">
          <Button onClick={() => setPreviewUrl(null)}>Close</Button>
        </div>
      </Modal>

      <Modal open={showModal} onClose={() => { setShowModal(false); reset(); }} title="New receipt" width="max-w-2xl">
        <form
          onSubmit={handleSubmit((d) => createMutation.mutate(buildReceiptPayload(d)))}
          className="flex flex-col gap-4"
        >
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-300">Supplier</label>
              <select className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3.5 py-2.5 text-sm text-gray-100 outline-none focus:border-brand-400" {...register("supplier_id")}>
                <option value="">— Select —</option>
                {suppliers.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-300">Destination location</label>
              <select className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3.5 py-2.5 text-sm text-gray-100 outline-none focus:border-brand-400" {...register("dest_location_id")}>
                <option value="">— Select —</option>
                {locations.map((l) => <option key={l.id} value={l.id}>{l.warehouse_name} / {l.name}</option>)}
              </select>
            </div>
          </div>
          <Input label="Receipt date" type="date" {...register("scheduled_date")} />

          <div className="border-t border-gray-800 pt-4">
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm font-medium text-gray-300">Products</p>
              <button type="button" onClick={() => append({ product_id: "", demand_qty: "" })}
                className="text-xs text-brand-400 hover:text-brand-100 transition-colors">+ Add line</button>
            </div>
            {fields.map((field, i) => (
              <div key={field.id} className="flex gap-3 mb-2 items-end">
                <div className="flex-1 flex flex-col gap-1.5">
                  <label className="text-xs text-gray-500">Product</label>
                  <select className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-100 outline-none focus:border-brand-400" {...register(`moves.${i}.product_id`)}>
                    <option value="">— Select —</option>
                    {products.map((p) => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
                  </select>
                </div>
                <div className="w-28">
                  <Input label="Qty" type="number" step="0.01" placeholder="0.00" {...register(`moves.${i}.demand_qty`)} />
                </div>
                {fields.length > 1 && (
                  <button type="button" onClick={() => remove(i)} className="mb-0.5 text-red-400 hover:text-red-300 transition-colors">
                    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                )}
              </div>
            ))}
          </div>

          {createMutation.isError && (
            <p className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400 border border-red-500/20">
              {((createMutation.error as any)?.response?.data?.detail) || "Failed to create receipt."}
            </p>
          )}
          <div className="flex gap-3 pt-1">
            <Button variant="ghost" type="button" onClick={() => { setShowModal(false); reset(); }}>Cancel</Button>
            <Button type="submit" loading={createMutation.isPending}>Create receipt</Button>
          </div>
        </form>
      </Modal>

      <ToastContainer toasts={toasts} dismiss={dismiss} />
    </div>
  );
}
