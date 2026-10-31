// FinVault AI — All TypeScript type definitions

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  monthly_income: number;
  currency: string;
  created_at: string;
}

export interface Expense {
  id: string;
  amount: number;
  category: string;
  description?: string;
  transaction_date: string;
  payment_method?: string;
  tags: string[];
  is_recurring: boolean;
  created_at: string;
}

export interface Income {
  id: string;
  amount: number;
  category: string;
  source?: string;
  description?: string;
  transaction_date: string;
  is_taxable: boolean;
  created_at: string;
}

export interface Loan {
  id: string;
  loan_name: string;
  loan_type: string;
  lender_name: string;
  loan_account_number?: string;
  principal_amount: number;
  annual_interest_rate: number;
  tenure_months: number;
  emi_amount: number;
  interest_method: string;
  disbursement_date: string;
  first_emi_date: string;
  emi_due_day: number;
  processing_fee: number;
  prepayment_penalty_percent: number;
  insurance_amount: number;
  outstanding_amount: number;
  total_emis_paid: number;
  total_emis_remaining?: number;
  status: "Active" | "Closed" | "Overdue" | "Foreclosed" | "Under Moratorium";
  is_co_applicant: boolean;
  co_applicant_name?: string;
  loan_manager_name?: string;
  loan_manager_phone?: string;
  customer_care_number?: string;
  branch_name?: string;
  notes?: string;
  created_at: string;
}

export interface LoanPayment {
  id: string;
  loan_id: string;
  emi_number: number;
  payment_date: string;
  due_date: string;
  amount_paid: number;
  principal_component: number;
  interest_component: number;
  outstanding_after_payment: number;
  payment_method?: string;
  transaction_id?: string;
  receipt_number?: string;
  is_prepayment: boolean;
  prepayment_amount: number;
  late_fee_paid: number;
  notes?: string;
  created_at: string;
}

export interface AmortizationRow {
  emi_number: number;
  due_date: string;
  emi_amount: number;
  principal_component: number;
  interest_component: number;
  outstanding_after: number;
  total_interest_paid: number;
  total_principal_paid: number;
}

export interface AmortizationSchedule {
  loan_id: string;
  summary: {
    principal: number;
    emi_amount: number;
    total_payment: number;
    total_interest: number;
    interest_to_principal_ratio: number;
    effective_cost: number;
    break_even_month: number;
  };
  schedule: AmortizationRow[];
}

export interface Budget {
  id: string;
  category: string;
  amount: number;
  month: number;
  year: number;
  created_at: string;
}

export interface EMIAlert {
  loan_id: string;
  loan_name: string;
  lender_name: string;
  emi_amount: number;
  due_date: string;
  days_remaining: number;
  severity: "warning" | "critical";
}

export interface BudgetWarning {
  category: string;
  budgeted: number;
  spent: number;
  utilisation_pct: number;
  is_over_budget: boolean;
  severity: "warning" | "critical";
}

export interface DashboardData {
  total_income_this_month: number;
  total_expenses_this_month: number;
  net_savings_this_month: number;
  savings_rate: number;
  total_active_loans: number;
  total_outstanding_debt: number;
  total_monthly_emi: number;
  foir: number;
  upcoming_emi_alerts: EMIAlert[];
  budget_warnings: BudgetWarning[];
  top_expense_categories: Array<{ category: string; amount: number; percentage: number }>;
  income_expense_trend: Array<{ month: string; income: number; expense: number; savings: number }>;
  ai_insight?: {
    health_score: number;
    score_reason: string;
    summary: string;
    top_concern: string;
    top_action: string;
  };
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}