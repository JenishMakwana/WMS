import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router-dom";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = (data: FormData) => {
    login.mutate({ username: data.email, password: data.password });
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to your CoreInventory account"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
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
          placeholder="••••••••"
          autoComplete="current-password"
          error={errors.password?.message}
          {...register("password")}
        />

        <div className="flex justify-end">
          <Link
            to="/auth/forgot-password"
            className="text-sm text-brand-400 hover:text-brand-100 transition-colors"
          >
            Forgot password?
          </Link>
        </div>

        {login.error && (
          <p className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400 border border-red-500/20">
            {(login.error as any).response?.data?.detail === "LOGIN_BAD_CREDENTIALS"
              ? "Invalid email or password. Please try again."
              : (login.error as any).response?.data?.detail || "Connection to server failed. Please check if backend is running."}
          </p>
        )}

        <Button type="submit" loading={login.isPending} className="mt-1">
          Sign in
        </Button>

        <p className="text-center text-sm text-gray-500">
          Don't have an account?{" "}
          <Link
            to="/auth/register"
            className="text-brand-400 hover:text-brand-100 transition-colors"
          >
            Create one
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}
