export interface User {
  id: string;
  email: string;
  name?: string;
  display_name?: string;
  role: string;
  status?: string;
  organization_id?: string;
  workspace_id?: string;
  is_active?: boolean;
  created_at?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  apiKey: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
