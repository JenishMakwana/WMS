import { clsx } from "clsx";

interface KpiCardProps {
  label: string;
  value: string | number;
  sub?: string;
  variant?: "default" | "warning" | "danger" | "success";
  onClick?: () => void;
}

const variantStyles = {
  default: "border-gray-800 bg-gray-900",
  warning: "border-amber-500/20 bg-amber-500/5",
  danger:  "border-red-500/20  bg-red-500/5",
  success: "border-green-500/20 bg-green-500/5",
};

const valueStyles = {
  default: "text-white",
  warning: "text-amber-400",
  danger:  "text-red-400",
  success: "text-green-400",
};

export function KpiCard({ label, value, sub, variant = "default", onClick }: KpiCardProps) {
  return (
    <div
      onClick={onClick}
      className={clsx(
        "rounded-xl border px-5 py-4 transition-all",
        variantStyles[variant],
        onClick && "cursor-pointer hover:border-gray-600"
      )}
    >
      <p className="text-xs text-gray-500 mb-2">{label}</p>
      <p className={clsx("text-2xl font-semibold tabular-nums", valueStyles[variant])}>{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  );
}
