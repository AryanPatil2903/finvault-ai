/**
 * Finance state store — loans, expenses, dashboard summary.
 */

import { create } from "zustand";
import type { DashboardData, Expense, Income, Loan } from "@/types";
import { dashboardApi, expenseApi, incomeApi, loanApi } from "@/services/api";

interface FinanceState {
  dashboard: DashboardData | null;
  expenses: Expense[];
  incomes: Income[];
  loans: Loan[];
  isLoading: boolean;
  error: string | null;
  fetchDashboard: () => Promise<void>;
  fetchExpenses: () => Promise<void>;
  fetchIncomes: () => Promise<void>;
  fetchLoans: () => Promise<void>;
}

export const useFinanceStore = create<FinanceState>((set) => ({
  dashboard: null,
  expenses: [],
  incomes: [],
  loans: [],
  isLoading: false,
  error: null,

  fetchDashboard: async () => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await dashboardApi.getSummary();
      set({ dashboard: data });
    } catch (e: any) {
      set({ error: e.message });
    } finally {
      set({ isLoading: false });
    }
  },

  fetchExpenses: async () => {
    const { data } = await expenseApi.list({ limit: 100 });
    set({ expenses: data });
  },

  fetchIncomes: async () => {
    const { data } = await incomeApi.list();
    set({ incomes: data });
  },

  fetchLoans: async () => {
    const { data } = await loanApi.list();
    set({ loans: data });
  },
}));