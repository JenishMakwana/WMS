import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router-dom";
import { productApi, categoryApi, locationApi } from "@/api/inventory";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { formatNumber } from "@/utils/format";

const schema = z.object({
  name: z.string().min(1, "Required"),
  sku: z.string().min(1, "Required"),
  unit_of_measure: z.string().min(1, "Required"),
  category_id: z.string().optional(),
  quantity: z.string().optional(),
  initial_location_id: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

export default function ProductsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);

  const { data: products = [], isLoading } = useQuery({
    queryKey: ["products", search],
    queryFn: () => productApi.list({ search: search || undefined }),
  });
  const { data: categories = [] } = useQuery({ queryKey: ["categories"], queryFn: categoryApi.list });
  const { data: locations = [] } = useQuery({ queryKey: ["locations"], queryFn: () => locationApi.list() });

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const createMutation = useMutation({
    mutationFn: (data: FormData) => productApi.create({
      ...data,
      quantity: data.quantity ? data.quantity : undefined,
      initial_location_id: data.initial_location_id || undefined,
      category_id: data.category_id || undefined,
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["products"] }); setShowModal(false); reset(); },
  });

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="Products"
        subtitle="Manage your product catalogue and stock availability"
        action={
          <Button onClick={() => setShowModal(true)} className="w-auto px-4">
            + New product
          </Button>
        }
      />

      {/* Filters */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-800">
        <div className="relative flex-1 max-w-sm">
          <svg viewBox="0 0 24 24" className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" fill="none" stroke="currentColor" strokeWidth={2}>
            <circle cx="11" cy="11" r="8" /><path strokeLinecap="round" d="m21 21-4.35-4.35" />
          </svg>
          <input
            className="w-full rounded-lg border border-gray-700 bg-gray-900 py-2 pl-9 pr-3 text-sm text-gray-100 placeholder:text-gray-500 outline-none focus:border-brand-400"
            placeholder="Search by name or SKU…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto px-6 py-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-20 text-gray-500 text-sm">Loading…</div>
        ) : products.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <p className="text-gray-500 text-sm">No products found.</p>
            <button onClick={() => setShowModal(true)} className="mt-3 text-sm text-brand-400 hover:text-brand-100 transition-colors">
              Create your first product
            </button>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-left text-xs text-gray-500 uppercase tracking-wide">
                <th className="pb-3 font-medium">Product</th>
                <th className="pb-3 font-medium">SKU</th>
                <th className="pb-3 font-medium">Category</th>
                <th className="pb-3 font-medium text-right">On hand</th>
                <th className="pb-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {products.map((p) => (
                <tr key={p.id} className="group hover:bg-gray-800/40 transition-colors">
                  <td className="py-3 pr-4">
                    <Link to={`/products/${p.id}`} className="font-medium text-gray-100 hover:text-brand-400 transition-colors">
                      {p.name}
                    </Link>
                  </td>
                  <td className="py-3 pr-4 font-mono text-gray-400">{p.sku}</td>
                  <td className="py-3 pr-4 text-gray-400">{p.category_name ?? "—"}</td>
                  <td className="py-3 pr-4 text-right font-medium text-gray-100">
                    {formatNumber(p.total_stock)} {p.unit_of_measure}
                  </td>
                  <td className="py-3">
                    {!p.is_active ? (
                      <Badge variant="neutral">Inactive</Badge>
                    ) : parseFloat(p.total_stock) === 0 ? (
                      <Badge variant="danger">Out of stock</Badge>
                    ) : (
                      <Badge variant="success">In stock</Badge>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Create Modal */}
      <Modal open={showModal} onClose={() => { setShowModal(false); reset(); }} title="New product">
        <form onSubmit={handleSubmit((d) => createMutation.mutate(d))} className="flex flex-col gap-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <Input label="Product name" error={errors.name?.message} {...register("name")} />
            </div>
            <Input label="SKU / Code" placeholder="SR-001" error={errors.sku?.message} {...register("sku")} />
            <Input label="Unit of measure" placeholder="pcs, kg, l…" error={errors.unit_of_measure?.message} {...register("unit_of_measure")} />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-gray-300">Category</label>
            <select className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3.5 py-2.5 text-sm text-gray-100 outline-none focus:border-brand-400" {...register("category_id")}>
              <option value="">— None —</option>
              {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>

          <div className="border-t border-gray-800 pt-4">
            <p className="text-xs text-gray-500 mb-3">Initial stock (optional)</p>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Quantity" type="number" placeholder="0" {...register("quantity")} />
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-300">Location</label>
                <select className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3.5 py-2.5 text-sm text-gray-100 outline-none focus:border-brand-400" {...register("initial_location_id")}>
                  <option value="">— Select —</option>
                  {locations.map((l) => <option key={l.id} value={l.id}>{l.warehouse_name} / {l.name}</option>)}
                </select>
              </div>
            </div>
          </div>

          {createMutation.isError && (
            <p className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400 border border-red-500/20">
              Failed to create product. SKU may already exist.
            </p>
          )}
          <div className="flex gap-3 pt-1">
            <Button variant="ghost" type="button" onClick={() => { setShowModal(false); reset(); }}>Cancel</Button>
            <Button type="submit" loading={createMutation.isPending}>Create product</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
