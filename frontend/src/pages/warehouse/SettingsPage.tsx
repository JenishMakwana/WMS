import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { warehouseApi, locationApi, categoryApi } from "@/api/inventory";
import { supplierApi, customerApi } from "@/api/parties";
import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Badge } from "@/components/ui/Badge";
import type { Warehouse } from "@/types/inventory";

const whSchema = z.object({
  name: z.string().min(1, "Required"),
  short_code: z.string().min(1, "Required").max(20),
  address: z.string().optional(),
});

const locSchema = z.object({
  name: z.string().min(1, "Required"),
  short_code: z.string().min(1, "Required").max(20),
  warehouse_id: z.string().min(1, "Required"),
});

const catSchema = z.object({
  name: z.string().min(1, "Required").max(100),
  description: z.string().optional(),
});

const partySchema = z.object({
  name: z.string().min(1, "Required").max(200),
  contact_info: z.string().optional(),
  address: z.string().optional(),
});

type WhForm = z.infer<typeof whSchema>;
type LocForm = z.infer<typeof locSchema>;
type CatForm = z.infer<typeof catSchema>;
type PartyForm = z.infer<typeof partySchema>;

export default function SettingsPage() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<"inventory" | "partners" | "organization">("inventory");
  const [showWhModal, setShowWhModal] = useState(false);
  const [showLocModal, setShowLocModal] = useState(false);
  const [showCatModal, setShowCatModal] = useState(false);
  const [showSuppModal, setShowSuppModal] = useState(false);
  const [showCustModal, setShowCustModal] = useState(false);
  const [selectedWh, setSelectedWh] = useState<Warehouse | null>(null);

  const { data: warehouses = [], isLoading: whLoading } = useQuery({
    queryKey: ["warehouses"],
    queryFn: () => warehouseApi.list(),
  });
  const { data: locations = [] } = useQuery({
    queryKey: ["locations", selectedWh?.id],
    queryFn: () => locationApi.list(selectedWh?.id),
  });
  const { data: categories = [], isLoading: catLoading } = useQuery({
    queryKey: ["categories"],
    queryFn: () => categoryApi.list(),
  });
  const { data: suppliers = [], isLoading: suppLoading } = useQuery({
    queryKey: ["suppliers"],
    queryFn: () => supplierApi.list(),
  });
  const { data: customers = [], isLoading: custLoading } = useQuery({
    queryKey: ["customers"],
    queryFn: () => customerApi.list(),
  });

  const whForm = useForm<WhForm>({ resolver: zodResolver(whSchema) });
  const locForm = useForm<LocForm>({ resolver: zodResolver(locSchema) });
  const catForm = useForm<CatForm>({ resolver: zodResolver(catSchema) });
  const suppForm = useForm<PartyForm>({ resolver: zodResolver(partySchema) });
  const custForm = useForm<PartyForm>({ resolver: zodResolver(partySchema) });

  const createWh = useMutation({
    mutationFn: (d: WhForm) => warehouseApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["warehouses"] }); setShowWhModal(false); whForm.reset(); },
  });
  const deactivateWh = useMutation({
    mutationFn: (id: string) => warehouseApi.remove(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["warehouses"] }); setSelectedWh(null); },
  });
  const createLoc = useMutation({
    mutationFn: (d: LocForm) => locationApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["locations"] }); setShowLocModal(false); locForm.reset(); },
  });
  const deactivateLoc = useMutation({
    mutationFn: (id: string) => locationApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["locations"] }),
  });
  const createCat = useMutation({
    mutationFn: (d: CatForm) => categoryApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["categories"] }); setShowCatModal(false); catForm.reset(); },
  });
  const deleteCat = useMutation({
    mutationFn: (id: string) => categoryApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["categories"] }),
  });
  const createSupp = useMutation({
    mutationFn: (d: PartyForm) => supplierApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["suppliers"] }); setShowSuppModal(false); suppForm.reset(); },
  });
  const deleteSupp = useMutation({
    mutationFn: (id: string) => supplierApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["suppliers"] }),
  });
  const createCust = useMutation({
    mutationFn: (d: PartyForm) => customerApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["customers"] }); setShowCustModal(false); custForm.reset(); },
  });
  const deleteCust = useMutation({
    mutationFn: (id: string) => customerApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["customers"] }),
  });

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Settings" subtitle="Manage warehouses, locations, categories, suppliers and customers" />

      {/* Tab Navigation */}
      <div className="px-6 border-b border-gray-800 bg-gray-900/50">
        <div className="flex gap-8">
          {[
            { id: "inventory", label: "Inventory", icon: (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            )},
            { id: "partners", label: "Partners", icon: (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            )},
            { id: "organization", label: "Organization", icon: (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
            )},
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-brand-500 text-brand-400"
                  : "border-transparent text-gray-500 hover:text-gray-300"
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6 space-y-12">

        {activeTab === "organization" && (
          <section className="animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-base font-medium text-white">Product Categories</h2>
                <p className="text-sm text-gray-500">Group your products for better organization</p>
              </div>
              <Button className="w-auto px-4" onClick={() => setShowCatModal(true)}>+ Add category</Button>
            </div>

            {catLoading ? (
              <p className="text-sm text-gray-500">Loading...</p>
            ) : categories.length === 0 ? (
              <div className="rounded-xl border border-dashed border-gray-700 px-6 py-10 text-center">
                <p className="text-sm text-gray-500">No categories yet.</p>
                <button onClick={() => setShowCatModal(true)} className="mt-2 text-sm text-brand-400 hover:text-brand-100 transition-colors">
                  Create your first category
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {categories.map((cat) => (
                  <div key={cat.id} className="group relative rounded-xl border border-gray-800 bg-gray-900 p-4 hover:border-gray-700 transition-all">
                    <p className="font-medium text-gray-100">{cat.name}</p>
                    {cat.description && <p className="text-xs text-gray-500 mt-1 line-clamp-1">{cat.description}</p>}
                    <button
                      onClick={() => deleteCat.mutate(cat.id)}
                      className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 text-xs text-red-400 hover:text-red-300 transition-all"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {activeTab === "partners" && (
          <div className="space-y-12 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <section>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-medium text-white">Suppliers</h2>
                  <p className="text-sm text-gray-500">Manage companies you receive stock from</p>
                </div>
                <Button className="w-auto px-4" onClick={() => setShowSuppModal(true)}>+ Add supplier</Button>
              </div>

              {suppLoading ? (
                <p className="text-sm text-gray-500">Loading...</p>
              ) : suppliers.length === 0 ? (
                <div className="rounded-xl border border-dashed border-gray-700 px-6 py-10 text-center">
                  <p className="text-sm text-gray-500">No suppliers yet.</p>
                  <button onClick={() => setShowSuppModal(true)} className="mt-2 text-sm text-brand-400 hover:text-brand-100 transition-colors">
                    Create your first supplier
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  {suppliers.map((s) => (
                    <div key={s.id} className="group relative rounded-xl border border-gray-800 bg-gray-900 p-4 hover:border-gray-700 transition-all">
                      <p className="font-medium text-gray-100">{s.name}</p>
                      {s.contact_info && <p className="text-xs text-gray-500 mt-1 line-clamp-1">{s.contact_info}</p>}
                      <button
                        onClick={() => deleteSupp.mutate(s.id)}
                        className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 text-xs text-red-400 hover:text-red-300 transition-all"
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-medium text-white">Customers</h2>
                  <p className="text-sm text-gray-500">Manage companies you deliver stock to</p>
                </div>
                <Button className="w-auto px-4" onClick={() => setShowCustModal(true)}>+ Add customer</Button>
              </div>

              {custLoading ? (
                <p className="text-sm text-gray-500">Loading...</p>
              ) : customers.length === 0 ? (
                <div className="rounded-xl border border-dashed border-gray-700 px-6 py-10 text-center">
                  <p className="text-sm text-gray-500">No customers yet.</p>
                  <button onClick={() => setShowCustModal(true)} className="mt-2 text-sm text-brand-400 hover:text-brand-100 transition-colors">
                    Create your first customer
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  {customers.map((c) => (
                    <div key={c.id} className="group relative rounded-xl border border-gray-800 bg-gray-900 p-4 hover:border-gray-700 transition-all">
                      <p className="font-medium text-gray-100">{c.name}</p>
                      {c.contact_info && <p className="text-xs text-gray-500 mt-1 line-clamp-1">{c.contact_info}</p>}
                      <button
                        onClick={() => deleteCust.mutate(c.id)}
                        className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 text-xs text-red-400 hover:text-red-300 transition-all"
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}

        {activeTab === "inventory" && (
          <div className="space-y-12 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <section>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-medium text-white">Warehouses</h2>
                  <p className="text-sm text-gray-500">Physical storage facilities in your network</p>
                </div>
                <Button className="w-auto px-4" onClick={() => setShowWhModal(true)}>+ Add warehouse</Button>
              </div>

              {whLoading ? (
                <p className="text-sm text-gray-500">Loading...</p>
              ) : warehouses.length === 0 ? (
                <div className="rounded-xl border border-dashed border-gray-700 px-6 py-10 text-center">
                  <p className="text-sm text-gray-500">No warehouses yet.</p>
                  <button onClick={() => setShowWhModal(true)} className="mt-2 text-sm text-brand-400 hover:text-brand-100 transition-colors">
                    Create your first warehouse
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {warehouses.map((wh) => (
                    <div
                      key={wh.id}
                      onClick={() => setSelectedWh(wh.id === selectedWh?.id ? null : wh)}
                      className={`cursor-pointer rounded-xl border p-4 transition-all ${
                        selectedWh?.id === wh.id
                          ? "border-brand-600 bg-brand-600/10"
                          : "border-gray-800 bg-gray-900 hover:border-gray-700"
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-gray-100">{wh.name}</p>
                          <p className="text-xs text-gray-500 mt-0.5 font-mono">{wh.short_code}</p>
                          {wh.address && <p className="text-xs text-gray-400 mt-1">{wh.address}</p>}
                        </div>
                        <Badge variant={wh.is_active ? "success" : "neutral"}>
                          {wh.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                      {selectedWh?.id === wh.id && (
                        <button
                          onClick={(e) => { e.stopPropagation(); deactivateWh.mutate(wh.id); }}
                          className="mt-3 text-xs text-red-400 hover:text-red-300 transition-colors"
                        >
                          Deactivate warehouse
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-medium text-white">Locations</h2>
                  <p className="text-sm text-gray-500">
                    {selectedWh ? `Locations in ${selectedWh.name}` : "Select a warehouse to filter locations"}
                  </p>
                </div>
                <Button className="w-auto px-4" onClick={() => {
                  if (selectedWh) locForm.setValue("warehouse_id", selectedWh.id);
                  setShowLocModal(true);
                }}>
                  + Add location
                </Button>
              </div>

              {locations.length === 0 ? (
                <div className="rounded-xl border border-dashed border-gray-700 px-6 py-10 text-center">
                  <p className="text-sm text-gray-500">
                    {selectedWh ? "No locations in this warehouse yet." : "No locations found."}
                  </p>
                </div>
              ) : (
                <div className="rounded-xl border border-gray-800 bg-gray-900 overflow-hidden">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-800 text-left text-xs text-gray-500 uppercase tracking-wide">
                        <th className="px-5 py-3 font-medium">Name</th>
                        <th className="py-3 font-medium">Code</th>
                        <th className="py-3 font-medium">Warehouse</th>
                        <th className="py-3 font-medium">Status</th>
                        <th className="py-3 pr-5 font-medium"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800/60">
                      {locations.map((loc) => (
                        <tr key={loc.id} className="hover:bg-gray-800/30 transition-colors">
                          <td className="px-5 py-3 font-medium text-gray-100">{loc.name}</td>
                          <td className="py-3 font-mono text-gray-400">{loc.short_code}</td>
                          <td className="py-3 text-gray-400">{loc.warehouse_name}</td>
                          <td className="py-3">
                            <Badge variant={loc.is_active ? "success" : "neutral"}>
                              {loc.is_active ? "Active" : "Inactive"}
                            </Badge>
                          </td>
                          <td className="py-3 pr-5 text-right">
                            <button
                              onClick={() => deactivateLoc.mutate(loc.id)}
                              className="text-xs text-red-400 hover:text-red-300 transition-colors"
                            >
                              Deactivate
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>
        )}
      </div>
      {/* Category Modal */}
      <Modal open={showCatModal} onClose={() => { setShowCatModal(false); catForm.reset(); }} title="Add category">
        <form onSubmit={catForm.handleSubmit((d) => createCat.mutate(d))} className="flex flex-col gap-4">
          <Input label="Category name" placeholder="Electronics" error={catForm.formState.errors.name?.message} {...catForm.register("name")} />
          <Input label="Description" placeholder="Optional category description" {...catForm.register("description")} />
          <div className="flex gap-3 pt-1">
            <Button variant="ghost" type="button" onClick={() => { setShowCatModal(false); catForm.reset(); }}>Cancel</Button>
            <Button type="submit" loading={createCat.isPending}>Create category</Button>
          </div>
        </form>
      </Modal>

      {/* Warehouse Modal */}
      <Modal open={showWhModal} onClose={() => { setShowWhModal(false); whForm.reset(); }} title="Add warehouse">
        <form onSubmit={whForm.handleSubmit((d) => createWh.mutate(d))} className="flex flex-col gap-4">
          <Input label="Warehouse name" placeholder="Main Warehouse" error={whForm.formState.errors.name?.message} {...whForm.register("name")} />
          <Input label="Short code" placeholder="WH01" error={whForm.formState.errors.short_code?.message} {...whForm.register("short_code")} />
          <Input label="Address" placeholder="123 Main St, City" {...whForm.register("address")} />
          {createWh.isError && (
            <p className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400 border border-red-500/20">
              Short code already in use.
            </p>
          )}
          <div className="flex gap-3 pt-1">
            <Button variant="ghost" type="button" onClick={() => { setShowWhModal(false); whForm.reset(); }}>Cancel</Button>
            <Button type="submit" loading={createWh.isPending}>Create warehouse</Button>
          </div>
        </form>
      </Modal>

      {/* Location Modal */}
      <Modal open={showLocModal} onClose={() => { setShowLocModal(false); locForm.reset(); }} title="Add location">
        <form onSubmit={locForm.handleSubmit((d) => createLoc.mutate(d))} className="flex flex-col gap-4">
          <Input label="Location name" placeholder="Rack A" error={locForm.formState.errors.name?.message} {...locForm.register("name")} />
          <Input label="Short code" placeholder="RA" error={locForm.formState.errors.short_code?.message} {...locForm.register("short_code")} />
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-gray-300">Warehouse</label>
            <select
              className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3.5 py-2.5 text-sm text-gray-100 outline-none focus:border-brand-400"
              {...locForm.register("warehouse_id")}
            >
              <option value="">— Select warehouse —</option>
              {warehouses.map((wh) => <option key={wh.id} value={wh.id}>{wh.name}</option>)}
            </select>
            {locForm.formState.errors.warehouse_id && (
              <p className="text-xs text-red-400">{locForm.formState.errors.warehouse_id.message}</p>
            )}
          </div>
          <div className="flex flex-col gap-3 pt-1">
            {createLoc.isError && (
              <p className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400 border border-red-500/20">
                Failed to create location. Please try again.
              </p>
            )}
            <div className="flex gap-3">
              <Button variant="ghost" type="button" onClick={() => { setShowLocModal(false); locForm.reset(); }}>Cancel</Button>
              <Button type="submit" loading={createLoc.isPending}>Create location</Button>
            </div>
          </div>
        </form>
      </Modal>

      {/* Supplier Modal */}
      <Modal open={showSuppModal} onClose={() => { setShowSuppModal(false); suppForm.reset(); }} title="Add supplier">
        <form onSubmit={suppForm.handleSubmit((d) => createSupp.mutate(d))} className="flex flex-col gap-4">
          <Input label="Supplier name" placeholder="ACME Corp" error={suppForm.formState.errors.name?.message} {...suppForm.register("name")} />
          <Input label="Contact Info" placeholder="email@example.com, +123..." {...suppForm.register("contact_info")} />
          <Input label="Address" placeholder="123 Street, City" {...suppForm.register("address")} />
          <div className="flex gap-3 pt-1">
            <Button variant="ghost" type="button" onClick={() => { setShowSuppModal(false); suppForm.reset(); }}>Cancel</Button>
            <Button type="submit" loading={createSupp.isPending}>Create supplier</Button>
          </div>
        </form>
      </Modal>

      {/* Customer Modal */}
      <Modal open={showCustModal} onClose={() => { setShowCustModal(false); custForm.reset(); }} title="Add customer">
        <form onSubmit={custForm.handleSubmit((d) => createCust.mutate(d))} className="flex flex-col gap-4">
          <Input label="Customer name" placeholder="Retail Store #1" error={custForm.formState.errors.name?.message} {...custForm.register("name")} />
          <Input label="Contact Info" placeholder="email@example.com, +123..." {...custForm.register("contact_info")} />
          <Input label="Address" placeholder="456 Avenue, City" {...custForm.register("address")} />
          <div className="flex gap-3 pt-1">
            <Button variant="ghost" type="button" onClick={() => { setShowCustModal(false); custForm.reset(); }}>Cancel</Button>
            <Button type="submit" loading={createCust.isPending}>Create customer</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
