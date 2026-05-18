import { clsx } from "clsx";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
  variant?: "primary" | "ghost";
}

export function Button({
  children,
  loading,
  variant = "primary",
  className,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={clsx(
        "flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2.5",
        "text-sm font-medium transition-all duration-150 disabled:cursor-not-allowed",
        variant === "primary" && [
          "bg-brand-600 text-white hover:bg-brand-800",
          "disabled:bg-brand-600/40 disabled:text-white/50",
        ],
        variant === "ghost" && [
          "border border-gray-700 text-gray-300 hover:bg-gray-800",
          "disabled:opacity-50",
        ],
        className
      )}
      {...props}
    >
      {loading && (
        <svg
          className="h-4 w-4 animate-spin"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 3v3m0 12v3M4.22 4.22l2.12 2.12m11.32 11.32 2.12 2.12M3 12h3m12 0h3"
          />
        </svg>
      )}
      {children}
    </button>
  );
}
