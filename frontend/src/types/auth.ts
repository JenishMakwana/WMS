export type UserRole = "admin" | "inventory_manager" | "warehouse_staff";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

export interface LoginRequest {
  username: string; // fastapi-users uses 'username' for email
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}
