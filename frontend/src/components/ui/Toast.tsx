import { useState } from "react";
import type { AlertMessage } from "@/hooks/useAlerts";

export type ToastType = "info" | "success" | "warning" | "error" | "inventory";

export interface GenericToast {
  type: "info" | "success" | "warning" | "error";
  title: string;
  message: string;
}

export type ToastMessage = 
  | (AlertMessage & { _toastType: "inventory" })
  | (GenericToast & { _toastType: "generic" });

interface Toast {
  id: number;
  msg: ToastMessage;
}

let toastId = 0;

export function useToasts() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const push = (msg: AlertMessage | GenericToast) => {
    const id = ++toastId;
    // Determine the internal toast type for rendering
    const toastMsg: ToastMessage = ("product_id" in msg) 
      ? { ...msg, _toastType: "inventory" } 
      : { ...msg, _toastType: "generic" };

    setToasts((t) => [...t, { id, msg: toastMsg }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 5000);
  };

  const alert = (title: string, message: string, type: GenericToast["type"] = "info") => {
    push({ type, title, message });
  };

  const dismiss = (id: number) => setToasts((t) => t.filter((x) => x.id !== id));

  return { toasts, push, alert, dismiss };
}

export function ToastContainer({ toasts, dismiss }: { toasts: Toast[]; dismiss: (id: number) => void }) {
  if (toasts.length === 0) return null;
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full">
      {toasts.map(({ id, msg }) => {
        const isInventory = msg._toastType === "inventory";
        
        let bgColor = "bg-gray-900";
        let borderColor = "border-gray-800";
        let iconColor = "bg-blue-400";
        let title = "Notification";
        let description = "";

        if (isInventory) {
          borderColor = msg.is_out_of_stock ? "border-red-500/40" : "border-amber-500/40";
          iconColor = msg.is_out_of_stock ? "bg-red-400" : "bg-amber-400";
          title = msg.is_out_of_stock ? "Out of stock" : "Low stock";
          description = `${msg.product_name} (${msg.sku}) — ${msg.qty} remaining`;
        } else {
          title = msg.title;
          description = msg.message;
          switch (msg.type) {
            case "success":
              borderColor = "border-emerald-500/40";
              iconColor = "bg-emerald-400";
              break;
            case "error":
              borderColor = "border-red-500/40";
              iconColor = "bg-red-400";
              break;
            case "warning":
              borderColor = "border-amber-500/40";
              iconColor = "bg-amber-400";
              break;
            default:
              borderColor = "border-blue-500/40";
              iconColor = "bg-blue-400";
          }
        }

        return (
          <div
            key={id}
            className={`flex items-start gap-3 rounded-xl border px-4 py-3 shadow-2xl backdrop-blur-md ${bgColor} ${borderColor}`}
          >
            <div className={`mt-1 h-2 w-2 shrink-0 rounded-full ${iconColor}`} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-100">{title}</p>
              <p className="text-xs text-gray-400 mt-0.5 leading-relaxed">{description}</p>
            </div>
            <button 
              onClick={() => dismiss(id)} 
              className="text-gray-500 hover:text-gray-300 transition-colors p-0.5"
            >
              <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        );
      })}
    </div>
  );
}
