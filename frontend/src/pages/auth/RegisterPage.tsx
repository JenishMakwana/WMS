import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router-dom";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";

const schema = z.object({
  full_name: z.string().min(2, "Full name must be at least 2 characters"),
  email: z.string().email("Enter a valid email"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Must contain an uppercase letter")
    .regex(/[0-9]/, "Must contain a number"),
  role: z.enum(["inventory_manager", "warehouse_staff"]),
});

type FormData = z.infer<typeof schema>;

export default function RegisterPage() {
  const { register: registerAuth } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { role: "warehouse_staff" },
  });

  const onSubmit = (data: FormData) => {
    registerAuth.mutate(data);
  };

  return (
    <AuthLayout
      title="Create account"
      subtitle="Get started with CoreInventory"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <Input
          label="Full name"
          placeholder="John Smith"
          autoComplete="name"
          error={errors.full_name?.message}
          {...register("full_name")}
        />
        <Input
          label="Email"
          type="email"
          placeholder="you@company.com"
          autoComplete="email"
          error={errors.email?.message}
          {...register("email")}
        />
        <Input
          label="Password"
          type="password"
          placeholder="Min. 8 characters"
          autoComplete="new-password"
          error={errors.password?.message}
          {...register("password")}
        />

        {/* Role selector */}
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-gray-300">Role</label>
          <select
            className="w-full rounded-lg border border-gray-700 bg-gray-900 px-3.5 py-2.5
                       text-sm text-gray-100 outline-none focus:border-brand-400
                       focus:ring-2 focus:ring-brand-400/20 transition-colors"
            {...register("role")}
          >
            <option value="warehouse_staff">Warehouse Staff</option>
            <option value="inventory_manager">Inventory Manager</option>
          </select>
          {errors.role && (
            <p className="text-xs text-red-400">{errors.role.message}</p>
          )}
        </div>

        {registerAuth.error && (
          <p className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400 border border-red-500/20">
            {(registerAuth.error as any).response?.data?.detail === "REGISTER_USER_ALREADY_EXISTS"
              ? "This email is already registered. Please sign in instead."
              : (registerAuth.error as any).response?.data?.detail || "Registration failed. Please check your connection."}
          </p>
        )}

        <Button type="submit" loading={registerAuth.isPending} className="mt-1">
          Create account
        </Button>

        <p className="text-center text-sm text-gray-500">
          Already have an account?{" "}
          <Link
            to="/auth/login"
            className="text-brand-400 hover:text-brand-100 transition-colors"
          >
            Sign in
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}
