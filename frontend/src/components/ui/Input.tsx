import { forwardRef } from "react";
import { clsx } from "clsx";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1.5">
        <label className="text-sm font-medium text-gray-300">{label}</label>
        <input
          ref={ref}
          className={clsx(
            "w-full rounded-lg border bg-gray-900 px-3.5 py-2.5 text-sm text-gray-100",
            "placeholder:text-gray-500 outline-none transition-colors",
            "focus:border-brand-400 focus:ring-2 focus:ring-brand-400/20",
            error
              ? "border-red-500 focus:border-red-500 focus:ring-red-500/20"
              : "border-gray-700",
            className
          )}
          {...props}
        />
        {error && <p className="text-xs text-red-400">{error}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";
