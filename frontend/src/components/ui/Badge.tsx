import { clsx } from "clsx";

type BadgeVariant = "success" | "warning" | "danger" | "neutral" | "info";

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const styles: Record<BadgeVariant, string> = {
  success: "bg-green-500/10 text-green-400 border border-green-500/20",
  warning: "bg-amber-500/10 text-amber-400 border border-amber-500/20",
  danger:  "bg-red-500/10  text-red-400  border border-red-500/20",
  neutral: "bg-gray-500/10 text-gray-400 border border-gray-700",
  info:    "bg-brand-600/10 text-brand-400 border border-brand-600/20",
};

export function Badge({ variant = "neutral", children, className }: BadgeProps) {
  return (
    <span className={clsx("inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium", styles[variant], className)}>
      {children}
    </span>
  );
}
