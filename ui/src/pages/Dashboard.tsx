/**
 * Main dashboard page — loads summary data and renders all widgets.
 */

import { useEffect } from "react";
import {
  AlertTriangle, Bot, CreditCard,
  PiggyBank, TrendingDown, TrendingUp, Wallet,
} from "lucide-react";
import {
  Area, AreaChart, CartesianGrid, Cell, Pie,
  PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import StatsCard from "@/components/Dashboard/StatsCard";
import { useFinanceStore } from "@/store/financeStore";

const COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"];

function formatINR(n: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency", currency: "INR", maximumFractionDigits: 0,
  }).format(n);
}

export default function Dashboard() {
  const { dashboard, fetchDashboard, isLoading } = useFinanceStore();

  useEffect(() => { fetchDashboard(); }, [fetchDashboard]);

  if (isLoading && !dashboard) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  if (!dashboard) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Financial Dashboard</h1>
        <p className="text-sm text-gray-500 mt-0.5">Your complete financial health at a glance</p>
      </div>

      {/* ── Alert Banners ─────────────────────────────────────────────── */}
      {dashboard.upcoming_emi_alerts.length > 0 && (
        <div className="space-y-2">
          {dashboard.upcoming_emi_alerts.map((alert) => (
            <div
              key={alert.loan_id}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium ${
                alert.severity === "critical"
                  ? "bg-danger-100 text-danger-500 border border-danger-200"
                  : "bg-warning-100 text-warning-500 border border-warning-200"
              }`}
            >
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span>
                <strong>{alert.loan_name}</strong> EMI of {formatINR(alert.emi_amount)} due{" "}
                {alert.days_remaining === 0 ? "today" : `in ${alert.days_remaining} day${alert.days_remaining !== 1 ? "s" : ""}`}
                {" "}— {new Date(alert.due_date).toLocaleDateString("en-IN")}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* ── Stats Cards ───────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatsCard
          title="Monthly Income"
          value={formatINR(dashboard.total_income_this_month)}
          icon={TrendingUp}
          iconColor="text-success-500"
          iconBg="bg-success-100"
        />
        <StatsCard
          title="Monthly Expenses"
          value={formatINR(dashboard.total_expenses_this_month)}
          icon={TrendingDown}
          iconColor="text-danger-500"
          iconBg="bg-danger-100"
        />
        <StatsCard
          title="Net Savings"
          value={formatINR(dashboard.net_savings_this_month)}
          subtitle={`${dashboard.savings_rate}% savings rate`}
          icon={PiggyBank}
          iconColor="text-brand-600"
          iconBg="bg-brand-100"
        />
        <StatsCard
          title="Total EMI Burden"
          value={formatINR(dashboard.total_monthly_emi)}
          subtitle={`FOIR: ${dashboard.foir}% | ${dashboard.total_active_loans} active loans`}
          icon={CreditCard}
          iconColor={dashboard.foir > 50 ? "text-danger-500" : "text-warning-500"}
          iconBg={dashboard.foir > 50 ? "bg-danger-100" : "bg-warning-100"}
        />
      </div>

      {/* ── AI Insight ────────────────────────────────────────────────── */}
      {dashboard.ai_insight && (
        <div className="bg-gradient-to-r from-brand-900 to-brand-700 rounded-xl p-6 text-white">
          <div className="flex items-start gap-4">
            <div className="bg-white/20 p-2 rounded-lg">
              <Bot className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h3 className="font-semibold text-lg">AI Financial Insight</h3>
                <div className="flex items-center gap-2 bg-white/20 px-3 py-1 rounded-full">
                  <span className="text-sm font-bold">{dashboard.ai_insight.health_score}/100</span>
                  <span className="text-xs text-white/70">health score</span>
                </div>
              </div>
              <p className="text-white/80 text-sm mb-3">{dashboard.ai_insight.summary}</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-white/10 rounded-lg p-3">
                  <p className="text-xs text-white/60 font-medium uppercase mb-1">⚠ Top Concern</p>
                  <p className="text-sm">{dashboard.ai_insight.top_concern}</p>
                </div>
                <div className="bg-white/10 rounded-lg p-3">
                  <p className="text-xs text-white/60 font-medium uppercase mb-1">✅ Action Item</p>
                  <p className="text-sm">{dashboard.ai_insight.top_action}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Charts Row ────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Income vs Expense Trend */}
        <div className="xl:col-span-2 bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Income vs Expenses (6 months)</h3>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={dashboard.income_expense_trend}>
              <defs>
                <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="expenseGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
              <Tooltip formatter={(v: number) => formatINR(v)} />
              <Area type="monotone" dataKey="income" stroke="#22c55e" fill="url(#incomeGrad)" strokeWidth={2} name="Income" />
              <Area type="monotone" dataKey="expense" stroke="#ef4444" fill="url(#expenseGrad)" strokeWidth={2} name="Expense" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Top Expense Categories Pie */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Expense Breakdown</h3>
          {dashboard.top_expense_categories.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={dashboard.top_expense_categories}
                    dataKey="amount"
                    nameKey="category"
                    cx="50%" cy="50%"
                    outerRadius={80}
                  >
                    {dashboard.top_expense_categories.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => formatINR(v)} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2 mt-2">
                {dashboard.top_expense_categories.map((cat, i) => (
                  <div key={cat.category} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
                      <span className="text-gray-600 truncate max-w-[120px]">{cat.category}</span>
                    </div>
                    <span className="font-medium text-gray-900">{cat.percentage.toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="text-gray-400 text-sm text-center py-8">No expenses recorded this month.</p>
          )}
        </div>
      </div>

      {/* ── Outstanding Debt Summary ───────────────────────────────────── */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-3">
          <Wallet className="w-5 h-5 text-brand-600" />
          <div>
            <h3 className="font-semibold text-gray-900">Total Outstanding Debt</h3>
            <p className="text-3xl font-bold text-danger-500 mt-1">
              {formatINR(dashboard.total_outstanding_debt)}
            </p>
          </div>
          <div className="ml-auto text-right">
            <p className="text-sm text-gray-500">across {dashboard.total_active_loans} active loans</p>
            <p className="text-sm font-medium text-gray-700">
              {formatINR(dashboard.total_monthly_emi)}/month in EMIs
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}