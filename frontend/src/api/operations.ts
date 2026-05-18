import api from "./client";
import type { LedgerEntry, Operation, OperationListItem, OperationStatus, OperationType } from "@/types/operations";

export const operationApi = {
  list: (params?: { type?: OperationType; status?: OperationStatus; search?: string }) =>
    api.get<OperationListItem[]>("/operations/", { params }).then((r) => r.data),

  get: (id: string) =>
    api.get<Operation>(`/operations/${id}`).then((r) => r.data),

  create: (data: Record<string, unknown>) =>
    api.post<Operation>("/operations/", data).then((r) => r.data),

  update: (id: string, data: Record<string, unknown>) =>
    api.patch<Operation>(`/operations/${id}`, data).then((r) => r.data),

  addMove: (id: string, data: Record<string, unknown>) =>
    api.post<Operation>(`/operations/${id}/moves`, data).then((r) => r.data),

  removeMove: (id: string, moveId: string) =>
    api.delete<Operation>(`/operations/${id}/moves/${moveId}`).then((r) => r.data),

  confirm: (id: string) =>
    api.post<Operation>(`/operations/${id}/confirm`).then((r) => r.data),

  validate: (id: string) =>
    api.post<Operation>(`/operations/${id}/validate`).then((r) => r.data),

  cancel: (id: string) =>
    api.post<Operation>(`/operations/${id}/cancel`).then((r) => r.data),

  downloadPdf: async (id: string, reference: string) => {
    const response = await api.get(`/operations/${id}/pdf`, {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `invoice_${reference.replace("/", "_")}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  getPdfBlob: async (id: string) => {
    const response = await api.get(`/operations/${id}/pdf`, {
      responseType: "blob",
    });
    return new Blob([response.data], { type: "application/pdf" });
  },

  ledger: (params?: { product_id?: string; location_id?: string; type?: OperationType; limit?: number }) =>
    api.get<LedgerEntry[]>("/operations/ledger", { params }).then((r) => r.data),
};
