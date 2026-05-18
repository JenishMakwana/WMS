import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { operationApi } from "@/api/operations";
import { productApi } from "@/api/inventory";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { StatusBadge, TypeBadge } from "@/components/operations/StatusBadge";
import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { Modal } from "@/components/ui/Modal";
import { formatDate, formatNumber } from "@/utils/format";

import { useToasts, ToastContainer } from "@/components/ui/Toast";

export default function OperationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { alert, toasts, dismiss } = useToasts();
  const [addingLine, setAddingLine] = useState(false);
  const [printing, setPrinting] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    return () => { if (previewUrl) window.URL.revokeObjectURL(previewUrl); };
  }, [previewUrl]);

  const { data: op, isLoading } = useQuery({
    queryKey: ["operation", id],
    queryFn: () => operationApi.get(id!),
    enabled: !!id,
  });
  const { data: products = [] } = useQuery({ queryKey: ["products"], queryFn: () => productApi.list() });
  const { register, handleSubmit, reset: resetForm } = useForm({ defaultValues: { product_id: "", demand_qty: "" } });

  const confirmMutation = useMutation({
    mutationFn: () => operationApi.confirm(id!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["operation", id] }),
  });
  const validateMutation = useMutation({
    mutationFn: () => operationApi.validate(id!),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["operation", id] }); qc.invalidateQueries({ queryKey: ["products"] }); },
  });
  const cancelMutation = useMutation({
    mutationFn: () => operationApi.cancel(id!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["operation", id] }),
  });
  const addMoveMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => operationApi.addMove(id!, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["operation", id] }); setAddingLine(false); resetForm(); },
  });
  const removeMoveMutation = useMutation({
    mutationFn: (moveId: string) => operationApi.removeMove(id!, moveId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["operation", id] }),
  });

  const handlePreview = async () => {
    if (!op) return;
    setPrinting(true);
    try {
      const blob = await operationApi.getPdfBlob(op.id);
      const url = window.URL.createObjectURL(blob);
      setPreviewUrl(url);
    } catch (err) {
      console.error("Failed to generate preview", err);
      alert("Error", "Could not generate PDF preview. Please check if the operation has product lines.", "error");
    } finally {
      setPrinting(false);
    }
  };

  if (isLoading) return <div className="flex items-center justify-center py-20 text-gray-500 text-sm">Loading…</div>;
  if (!op) return <div className="flex items-center justify-center py-20 text-gray-500 text-sm">Operation not found.</div>;

  const isDraft = op.status === "DRAFT";
  const isConfirmed = op.status === "CONFIRMED";
  const isDone = op.status === "DONE";
  const isCancelled = op.status === "CANCELLED";
  const backPath = op.type === "RECEIPT" ? "/receipts" : op.type === "DELIVERY" ? "/deliveries" : "/operations";

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title={op.reference}
        subtitle={op.supplier_name ?? op.customer_name ?? op.supplier ?? op.customer ?? ""}
        action={
          <div className="flex gap-2 flex-wrap justify-end">
            <Button variant="ghost" className="w-auto px-3" onClick={() => navigate(backPath)}>← Back</Button>
            <Button variant="ghost" className="w-auto px-3 text-brand-400" onClick={handlePreview} loading={printing}>
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Preview
            </Button>
            {isDraft && (
              <>
                <Button variant="ghost" className="w-auto px-3 text-red-400" onClick={() => cancelMutation.mutate()} loading={cancelMutation.isPending}>Cancel</Button>
                <Button className="w-auto px-4" onClick={() => confirmMutation.mutate()} loading={confirmMutation.isPending}>Confirm</Button>
              </>
            )}
            {isConfirmed && (
              <>
                <Button variant="ghost" className="w-auto px-3 text-red-400" onClick={() => cancelMutation.mutate()} loading={cancelMutation.isPending}>Cancel</Button>
                <Button className="w-auto px-4 bg-green-600 hover:bg-green-700" onClick={() => validateMutation.mutate()} loading={validateMutation.isPending}>Validate →</Button>
              </>
            )}
          </div>
        }
      />

      <div className="flex-1 overflow-auto p-6 space-y-6">
        {/* Error messages */}
        {(validateMutation.isError || confirmMutation.isError || cancelMutation.isError || addMoveMutation.isError) && (
          <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-5 py-4 text-sm text-red-400">
            {((validateMutation.error as any)?.response?.data?.detail) ||
              ((confirmMutation.error as any)?.response?.data?.detail) ||
              ((cancelMutation.error as any)?.response?.data?.detail) ||
              ((addMoveMutation.error as any)?.response?.data?.detail) ||
              "An error occurred. Please try again."}
          </div>
        )}

        {/* Meta cards */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
          {[
            { label: "Type", value: <TypeBadge type={op.type} /> },
            { label: "Status", value: <StatusBadge status={op.status} /> },
            { label: op.type === "RECEIPT" ? "Source (supplier)" : "Destination (customer)", value: op.supplier_name ?? op.customer_name ?? op.supplier ?? op.customer ?? "—" },
            { label: op.type === "RECEIPT" ? "Supplier Address" : "Customer Address", value: op.supplier_address ?? op.customer_address ?? "—" },
            { label: "Scheduled Date", value: formatDate(op.scheduled_date ?? op.created_at) },
            { label: op.type === "INTERNAL" ? "From → To" : op.type === "RECEIPT" ? "Destination" : "Source",
              value: op.type === "INTERNAL"
                ? `${op.src_location_name ?? "?"} → ${op.dest_location_name ?? "?"}`
                : (op.dest_location_name ?? op.src_location_name ?? "—") },
          ].map((c) => (
            <div key={c.label} className="rounded-xl border border-gray-800 bg-gray-900 px-5 py-4">
              <p className="text-xs text-gray-500 mb-1">{c.label}</p>
              <div className="text-sm font-medium text-gray-100">{c.value}</div>
            </div>
          ))}
        </div>

        {/* Product lines */}
        <div className="rounded-xl border border-gray-800 bg-gray-900">
          <div className="flex items-center justify-between border-b border-gray-800 px-5 py-4">
            <h3 className="text-sm font-medium text-gray-100">Product lines</h3>
            {isDraft && (
              <button onClick={() => setAddingLine(!addingLine)} className="text-xs text-brand-400 hover:text-brand-100 transition-colors">
                {addingLine ? "Cancel" : "+ Add line"}
              </button>
            )}
          </div>

          {addingLine && (
            <form onSubmit={handleSubmit((d) => addMoveMutation.mutate(d as Record<string, unknown>))}
              className="flex gap-3 items-end px-5 py-3 border-b border-gray-800 bg-gray-800/40">
              <div className="flex-1">
                <label className="text-xs text-gray-500 mb-1 block">Product</label>
                <select className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-100 outline-none focus:border-brand-400" {...register("product_id", { required: true })}>
                  <option value="">— Select —</option>
                  {products.map((p) => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
                </select>
              </div>
              <div className="w-28">
                <label className="text-xs text-gray-500 mb-1 block">Qty</label>
                <input type="number" step="0.01" placeholder="0.00" className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-100 outline-none focus:border-brand-400" {...register("demand_qty", { required: true })} />
              </div>
              <Button type="submit" className="w-auto px-4" loading={addMoveMutation.isPending}>Add</Button>
            </form>
          )}

          {op.moves.length === 0 ? (
            <p className="px-5 py-6 text-sm text-gray-500">No product lines yet.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-xs text-gray-500 uppercase tracking-wide text-left">
                  <th className="px-5 py-3 font-medium">Product</th>
                  <th className="py-3 font-medium">SKU</th>
                  <th className="py-3 font-medium text-right">Demand qty</th>
                  <th className="py-3 font-medium text-right">Done qty</th>
                  {isDraft && <th className="py-3 pr-5 font-medium"></th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {op.moves.map((m) => (
                  <tr key={m.id} className="hover:bg-gray-800/30">
                    <td className="px-5 py-3 font-medium text-gray-100">{m.product_name}</td>
                    <td className="py-3 font-mono text-gray-400">{m.product_sku}</td>
                    <td className="py-3 text-right text-gray-100">{formatNumber(m.demand_qty)} {m.product_uom}</td>
                    <td className="py-3 text-right text-gray-400">
                      {m.done_qty ? `${formatNumber(m.done_qty)} ${m.product_uom}` : "—"}
                    </td>
                    {isDraft && (
                      <td className="py-3 pr-5 text-right">
                        <button onClick={() => removeMoveMutation.mutate(m.id)} className="text-xs text-red-400 hover:text-red-300">Remove</button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Validated info */}
        {isDone && op.validated_at && (
          <div className="rounded-xl border border-green-500/20 bg-green-500/5 px-5 py-4">
            <p className="text-sm text-green-400">
              Validated on {formatDate(op.validated_at)} — stock has been updated.
            </p>
          </div>
        )}
        {isCancelled && (
          <div className="rounded-xl border border-red-500/20 bg-red-500/5 px-5 py-4">
            <p className="text-sm text-red-400">This operation has been cancelled.</p>
          </div>
        )}
      </div>

      <Modal
        open={!!previewUrl}
        onClose={() => setPreviewUrl(null)}
        title={`Preview: ${op.reference}`}
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

      <ToastContainer toasts={toasts} dismiss={dismiss} />
    </div>
  );
}
