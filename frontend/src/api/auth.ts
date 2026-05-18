import api from "./client";
import type {
  AuthTokens,
  LoginRequest,
  RegisterRequest,
  User,
} from "@/types/auth";

export const authApi = {
  async login(data: LoginRequest): Promise<AuthTokens> {
    // fastapi-users login expects form data
    const form = new URLSearchParams();
    form.append("username", data.username);
    form.append("password", data.password);

    const res = await api.post<AuthTokens>("/auth/jwt/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return res.data;
  },

  async register(data: RegisterRequest): Promise<User> {
    const res = await api.post<User>("/auth/register", data);
    return res.data;
  },

  async me(): Promise<User> {
    const res = await api.get<User>("/auth/me");
    return res.data;
  },

  async forgotPassword(email: string): Promise<void> {
    await api.post("/auth/forgot-password", { email });
  },

  async resetPassword(token: string, password: string): Promise<void> {
    await api.post("/auth/reset-password", { token, password });
  },

  async logout(): Promise<void> {
    await api.post("/auth/jwt/logout");
    localStorage.removeItem("access_token");
  },
};
