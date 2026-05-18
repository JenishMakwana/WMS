import api from "./client";
import type { Category, Location, Product, ProductListItem, Warehouse } from "@/types/inventory";

// ── Warehouses ────────────────────────────────────────────────────────────────
export const warehouseApi = {
  list: () => api.get<Warehouse[]>("/warehouses/").then((r) => r.data),
  get: (id: string) => api.get<Warehouse>(`/warehouses/${id}`).then((r) => r.data),
  create: (data: Partial<Warehouse>) => api.post<Warehouse>("/warehouses/", data).then((r) => r.data),
  update: (id: string, data: Partial<Warehouse>) => api.patch<Warehouse>(`/warehouses/${id}`, data).then((r) => r.data),
  remove: (id: string) => api.delete(`/warehouses/${id}`),
};

// ── Locations ─────────────────────────────────────────────────────────────────
export const locationApi = {
  list: (warehouse_id?: string) =>
    api.get<Location[]>("/locations/", { params: warehouse_id ? { warehouse_id } : {} }).then((r) => r.data),
  create: (data: Partial<Location>) => api.post<Location>("/locations/", data).then((r) => r.data),
  update: (id: string, data: Partial<Location>) => api.patch<Location>(`/locations/${id}`, data).then((r) => r.data),
  remove: (id: string) => api.delete(`/locations/${id}`),
};

// ── Categories ────────────────────────────────────────────────────────────────
export const categoryApi = {
  list: () => api.get<Category[]>("/categories/").then((r) => r.data),
  create: (data: Partial<Category>) => api.post<Category>("/categories/", data).then((r) => r.data),
  update: (id: string, data: Partial<Category>) => api.patch<Category>(`/categories/${id}`, data).then((r) => r.data),
  remove: (id: string) => api.delete(`/categories/${id}`),
};

// ── Products ──────────────────────────────────────────────────────────────────
export const productApi = {
  list: (params?: { search?: string; category_id?: string; low_stock_only?: boolean }) =>
    api.get<ProductListItem[]>("/products/", { params }).then((r) => r.data),
  get: (id: string) => api.get<Product>(`/products/${id}`).then((r) => r.data),
  create: (data: Record<string, unknown>) => api.post<Product>("/products/", data).then((r) => r.data),
  update: (id: string, data: Record<string, unknown>) => api.patch<Product>(`/products/${id}`, data).then((r) => r.data),
  remove: (id: string) => api.delete(`/products/${id}`),
};
