import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useState } from "react";
import { categoryApi, productApi } from "@/api/inventory";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { formatNumber } from "@/utils/format";

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [editing, setEditing] = useState(false);

  const { data: product, isLoading } = useQuery({
    queryKey: ["product", id],
    queryFn: () => productApi.get(id!),
    enabled: !!id,
  });
  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: categoryApi.list,
  });

  const { register, handleSubmit, reset } = useForm({
    values: product
      ? {
          name: product.name,
          sku: product.sku,
          description: product.description ?? "",
          unit_of_measure: product.unit_of_measure,
          category_id: product.category_id ?? "",
          is_active: product.is_active,
        }
      : undefined,
  });

  const updateMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => productApi.update(id!, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["product", id] });
      qc.invalidateQueries({ queryKey: ["products"] });
      setEditing(false);
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: () => productApi.remove(id!),
    onSuccess: () => navigate("/products"),
  });

  if (isLoading) return <div className="flex items-center justify-center py-20 text-gray-500 text-sm">Loading…</div>;
  if (!product) return <div className="flex items-center justify-center py-20 text-gray-500 text-sm">Product not found.</div>;

  const totalStock = parseFloat(product.total_stock);

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title={product.name}
        subtitle={`SKU: ${product.sku}`}
        action={
          <div className="flex gap-2">
            <Button variant="ghost" className="w-auto px-3" onClick={() => navigate("/products")}>Back</Button>
            <Button variant="ghost" className="w-auto px-3" onClick={() => setEditing(true)}>Edit</Button>
            <Button variant="ghost" className="w-auto px-3 text-red-400 hover:text-red-300"
              onClick={() => deactivateMutation.mutate()} loading={deactivateMutation.isPending}>
              Deactivate
            </Button>
          </div>
        }
      />

      <div className="flex-1 overflow-auto p-6 space-y-6">
        {/* Info cards */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: "Total stock", value: `${formatNumber(totalStock)} ${product.unit_of_measure}` },
            { label: "Category", value: product.category_name ?? "-" },
            { label: "Status", value: totalStock === 0 ? <Badge variant="danger">Out of stock</Badge> : <Badge variant="success">In stock</Badge> },
          ].map((card) => (
            <div key={card.label} className="rounded-xl border border-gray-800 bg-gray-900 px-5 py-4">
              <p className="text-xs text-gray-500 mb-1">{card.label}</p>
              <p className="text-sm font-medium text-gray-100">{card.value}</p>
            </div>
          ))}
        </div>

        {/* Stock by location */}
        <div className="rounded-xl border border-gray-800 bg-gray-900">
          <div className="border-b border-gray-800 px-5 py-4">
            <h3 className="text-sm font-medium text-gray-100">Stock by location</h3>
          </div>
          {product.stock_by_location.length === 0 ? (
            <p className="px-5 py-6 text-sm text-gray-500">No stock recorded yet.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-left text-xs text-gray-500 uppercase tracking-wide">
                  <th className="px-5 pb-3 pt-3 font-medium">Warehouse</th>
                  <th className="pb-3 pt-3 font-medium">Location</th>
                  <th className="pb-3 pt-3 pr-5 font-medium text-right">Quantity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {product.stock_by_location.map((s) => (
                  <tr key={s.location_id} className="hover:bg-gray-800/30">
                    <td className="px-5 py-3 text-gray-400">{s.warehouse_name}</td>
                    <td className="py-3 text-gray-100 font-medium">{s.location_name}</td>
                    <td className="py-3 pr-5 text-right text-gray-100">
                      {formatNumber(s.quantity)} {product.unit_of_measure}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Edit drawer — inline for simplicity */}
      {editing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60" onClick={() => setEditing(false)} />
          <div className="relative w-full max-w-md rounded-2xl border border-gray-800 bg-gray-900 p-6">
            <h2 className="text-base font-semibold text-white mb-5">Edit product</h2>
            <form
              onSubmit={handleSubmit((d) =>
                updateMutation.mutate({
                  ...d,
                  category_id: d.category_id || null,
                })
              )}
              className="flex flex-col gap-4"
            >
              <Input label="Name" {...register("name")} />
              <Input label="SKU" {...register("sku")} />
              <Input label="Description" {...register("description")} />
              <Input label="Unit of measure" {...register("unit_of_measure")} />
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-gray-300">Category</label>
                <select
                  className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3.5 py-2.5 text-sm text-gray-100 outline-none focus:border-brand-400"
                  {...register("category_id")}
                >
                  <option value="">-- Select category --</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
              <label className="flex items-center gap-2 text-sm text-gray-300">
                <input type="checkbox" className="h-4 w-4 rounded border-gray-700 bg-gray-900" {...register("is_active")} />
                Active product
              </label>
              {updateMutation.isError && (
                <p className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400 border border-red-500/20">
                  {((updateMutation.error as any)?.response?.data?.detail) || "Failed to update product."}
                </p>
              )}
              <div className="flex gap-3 pt-1">
                <Button variant="ghost" type="button" onClick={() => { setEditing(false); reset(); }}>Cancel</Button>
                <Button type="submit" loading={updateMutation.isPending}>Save changes</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
