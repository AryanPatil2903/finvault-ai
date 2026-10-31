/**
 * Centralised API client built on axios.
 * Automatically attaches JWT Bearer token from localStorage.
 * Handles 401 → logout and error normalisation.
 */

import axios, { AxiosInstance, AxiosResponse } from "axios";
import type {
  AmortizationSchedule,
  Budget,
  ChatMessage,
  DashboardData,
  Expense,
  Income,
  Loan,
  LoanPayment,
  TokenResponse,
  User,
} from "@/types";

const BASE_URL = import.meta.env.VITE_API_URL || "/api/v1";

// ── Axios Instance ────────────────────────────────────────────────────────────
const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30_000,
});

// ── Request interceptor: attach token ─────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("finvault_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response interceptor: handle 401 ─────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("finvault_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: {
    full_name: string; email: string; password: string;
    phone?: string; monthly_income?: number;
  }): Promise<AxiosResponse<User>> =>
    api.post("/auth/register", data),

  login: (email: string, password: string): Promise<AxiosResponse<TokenResponse>> =>
    api.post("/auth/login", { email, password }),

  getMe: (): Promise<AxiosResponse<User>> =>
    api.get("/auth/me"),

  updateProfile: (data: Partial<User>): Promise<AxiosResponse<User>> =>
    api.patch("/auth/me", data),
};

// ── Expenses ──────────────────────────────────────────────────────────────────
export const expenseApi = {
  list: (params?: {
    category?: string; start_date?: string;
    end_date?: string; limit?: number; offset?: number;
  }): Promise<AxiosResponse<Expense[]>> =>
    api.get("/expenses", { params }),

  create: (data: Omit<Expense, "id" | "created_at">): Promise<AxiosResponse<Expense>> =>
    api.post("/expenses", data),

  update: (id: string, data: Partial<Expense>): Promise<AxiosResponse<Expense>> =>
    api.patch(`/expenses/${id}`, data),

  delete: (id: string): Promise<AxiosResponse<void>> =>
    api.delete(`/expenses/${id}`),
};

// ── Incomes ───────────────────────────────────────────────────────────────────
export const incomeApi = {
  list: (params?: { start_date?: string; end_date?: string }): Promise<AxiosResponse<Income[]>> =>
    api.get("/incomes", { params }),

  create: (data: Omit<Income, "id" | "created_at">): Promise<AxiosResponse<Income>> =>
    api.post("/incomes", data),

  delete: (id: string): Promise<AxiosResponse<void>> =>
    api.delete(`/incomes/${id}`),
};

// ── Loans ─────────────────────────────────────────────────────────────────────
export const loanApi = {
  list: (): Promise<AxiosResponse<Loan[]>> =>
    api.get("/loans"),

  create: (data: Partial<Loan>): Promise<AxiosResponse<Loan>> =>
    api.post("/loans", data),

  get: (id: string): Promise<AxiosResponse<Loan>> =>
    api.get(`/loans/${id}`),

  update: (id: string, data: Partial<Loan>): Promise<AxiosResponse<Loan>> =>
    api.patch(`/loans/${id}`, data),

  delete: (id: string): Promise<AxiosResponse<void>> =>
    api.delete(`/loans/${id}`),

  getAmortization: (id: string): Promise<AxiosResponse<AmortizationSchedule>> =>
    api.get(`/loans/${id}/amortization`),

  payNext: (loanId: string, payment_method?: string): Promise<AxiosResponse<LoanPayment>> =>
    api.post(`/loans/${loanId}/pay-next`, null, { params: { payment_method } }),

  recordPayment: (
    loanId: string,
    data: Partial<LoanPayment>
  ): Promise<AxiosResponse<LoanPayment>> =>
    api.post(`/loans/${loanId}/payments`, data),

  listPayments: (loanId: string): Promise<AxiosResponse<LoanPayment[]>> =>
    api.get(`/loans/${loanId}/payments`),

  getPrepaymentImpact: (
    loanId: string,
    amount: number
  ): Promise<AxiosResponse<any>> =>
    api.post(`/loans/${loanId}/prepayment-impact?prepayment_amount=${amount}`),

  calculateEMI: (data: {
    principal: number; annual_interest_rate: number;
    tenure_months: number; method?: string;
  }): Promise<AxiosResponse<any>> =>
    api.post("/loans/calculator/emi", data),
};

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const dashboardApi = {
  getSummary: (include_ai = true): Promise<AxiosResponse<DashboardData>> =>
    api.get(`/dashboard/summary?include_ai=${include_ai}`),
};

// ── Budgets ───────────────────────────────────────────────────────────────────
export const budgetApi = {
  list: (): Promise<AxiosResponse<Budget[]>> =>
    api.get("/budgets"),
  create: (data: Omit<Budget, "id" | "created_at">): Promise<AxiosResponse<Budget>> =>
    api.post("/budgets", data),
  delete: (id: string): Promise<AxiosResponse<void>> =>
    api.delete(`/budgets/${id}`),
};

// ── AI Chat ───────────────────────────────────────────────────────────────────
export const aiApi = {
  chat: (data: {
    message: string;
    conversation_id?: string;
    include_financial_context?: boolean;
  }): Promise<AxiosResponse<{ conversation_id: string; reply: string; messages: ChatMessage[] }>> =>
    api.post("/ai/chat", data),

  listConversations: (): Promise<AxiosResponse<any[]>> =>
    api.get("/ai/conversations"),
};

export default api;
