export type Role = null | "admin" | "seller" | "user";

export interface AuthTokens {
  access_token: string; // JWT dari backend
  token_type: string;
}

export interface Me {
  id: string;
  email: string;
  role: Role;
  is_active?: boolean;
}
