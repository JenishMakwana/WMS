import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/store/authStore";
import type { LoginRequest, RegisterRequest } from "@/types/auth";

export function useAuth() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { setToken, setUser, logout: clearStore, isAuthenticated } = useAuthStore();

  // Fetch current user when authenticated
  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isAuthenticated,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: async (tokens) => {
      setToken(tokens.access_token);
      const me = await authApi.me();
      setUser(me);
      navigate("/dashboard");
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: async (_, vars) => {
      // Auto-login after registration
      const tokens = await authApi.login({
        username: vars.email,
        password: vars.password,
      });
      setToken(tokens.access_token);
      const me = await authApi.me();
      setUser(me);
      navigate("/dashboard");
    },
  });

  const forgotPasswordMutation = useMutation({
    mutationFn: (email: string) => authApi.forgotPassword(email),
  });

  const resetPasswordMutation = useMutation({
    mutationFn: ({ token, password }: { token: string; password: string }) =>
      authApi.resetPassword(token, password),
    onSuccess: () => navigate("/auth/login"),
  });

  const logout = async () => {
    try {
      await authApi.logout();
    } catch {
      // ignore — clear locally regardless
    }
    clearStore();
    queryClient.clear();
    navigate("/auth/login");
  };

  return {
    user,
    userLoading,
    isAuthenticated,
    login: loginMutation,
    register: registerMutation,
    forgotPassword: forgotPasswordMutation,
    resetPassword: resetPasswordMutation,
    logout,
  };
}
