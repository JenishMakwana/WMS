import { Badge } from "@/components/ui/Badge";
import type { OperationStatus, OperationType } from "@/types/operations";

const statusMap: Record<OperationStatus, { label: string; variant: "success" | "warning" | "danger" | "neutral" | "info" }> = {
  DRAFT:     { label: "Draft",     variant: "neutral" },
  CONFIRMED: { label: "Confirmed", variant: "info" },
  DONE:      { label: "Done",      variant: "success" },
  CANCELLED: { label: "Cancelled", variant: "danger" },
};

const typeMap: Record<OperationType, string> = {
  RECEIPT:    "Receipt",
  DELIVERY:   "Delivery",
  INTERNAL:   "Transfer",
  ADJUSTMENT: "Adjustment",
};

export function StatusBadge({ status }: { status: OperationStatus }) {
  const { label, variant } = statusMap[status] ?? { label: status, variant: "neutral" };
  return <Badge variant={variant}>{label}</Badge>;
}

export function TypeBadge({ type }: { type: OperationType }) {
  const colors: Record<OperationType, string> = {
    RECEIPT:    "bg-teal-500/10 text-teal-400 border border-teal-500/20",
    DELIVERY:   "bg-purple-500/10 text-purple-400 border border-purple-500/20",
    INTERNAL:   "bg-amber-500/10 text-amber-400 border border-amber-500/20",
    ADJUSTMENT: "bg-gray-500/10 text-gray-400 border border-gray-700",
  };
  return (
    <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ${colors[type]}`}>
      {typeMap[type]}
    </span>
  );
}
