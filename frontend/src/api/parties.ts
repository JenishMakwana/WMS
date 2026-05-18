import api from "./client";
import type { Supplier, Customer } from "@/types/inventory";

export const supplierApi = {
  list: (active_only: boolean = true) => 
    api.get<Supplier[]>("/suppliers/", { params: { active_only } }).then((r) => r.data),
  get: (id: string) => api.get<Supplier>(`/suppliers/${id}`).then((r) => r.data),
  create: (data: Partial<Supplier>) => api.post<Supplier>("/suppliers/", data).then((r) => r.data),
  update: (id: string, data: Partial<Supplier>) => api.patch<Supplier>(`/suppliers/${id}`, data).then((r) => r.data),
  remove: (id: string) => api.delete(`/suppliers/${id}`),
};

export const customerApi = {
  list: (active_only: boolean = true) => 
    api.get<Customer[]>("/customers/", { params: { active_only } }).then((r) => r.data),
  get: (id: string) => api.get<Customer>(`/customers/${id}`).then((r) => r.data),
  create: (data: Partial<Customer>) => api.post<Customer>("/customers/", data).then((r) => r.data),
  update: (id: string, data: Partial<Customer>) => api.patch<Customer>(`/customers/${id}`, data).then((r) => r.data),
  remove: (id: string) => api.delete(`/customers/${id}`),
};
