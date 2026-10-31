/**
 * Loan summary card showing all key loan details at a glance.
 * Includes progress bar for repayment progress.
 */

import { Building2, Calendar, Phone, TrendingDown } from "lucide-react";
import type { Loan } from "@/types";

interface LoanCardProps {
  loan: Loan;
  onViewSchedule: (loan: Loan) => void;
  onRecordPayment: (loan: Loan) => void;
}

const statusColors: Record<string, string> = {
  Active: "bg-success-100 text-success-500",
  Closed: "bg-gray-100 text-gray-500",
  Overdue: "bg-danger-100 text-danger-500",
  Foreclosed: "bg-purple-100 text-purple-600",
  "Under Moratorium": "bg-warning-100 text-warning-500",
};

function formatINR(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency", currency: "INR", maximumFractionDigits: 0,
  }).format(amount);
}

export default function LoanCard({ loan, onViewSchedule, onRecordPayment }: LoanCardProps) {
  const progress = loan.total_emis_paid / loan.tenure_months * 100;
  const repaid = loan.principal_amount - loan.outstanding_amount;

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-gray-900 text-lg">{loan.loan_name}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-sm text-gray-500">{loan.loan_type}</span>
            <span className="text-gray-300">•</span>
            <span className="text-sm text-gray-500 flex items-center gap-1">
              <Building2 className="w-3.5 h-3.5" />{loan.lender_name}
            </span>
          </div>
        </div>
        <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${statusColors[loan.status] || "bg-gray-100 text-gray-600"}`}>
          {loan.status}
        </span>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-500 mb-0.5">Outstanding</p>
          <p className="font-bold text-danger-500">{formatINR(loan.outstanding_amount)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-0.5">EMI / Month</p>
          <p className="font-bold text-gray-900">{formatINR(loan.emi_amount)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-0.5">Interest Rate</p>
          <p className="font-bold text-gray-900">{loan.annual_interest_rate}% p.a.</p>
        </div>
      </div>

      {/* Repayment Progress */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-gray-500 mb-1.5">
          <span>{loan.total_emis_paid} of {loan.tenure_months} EMIs paid</span>
          <span>{progress.toFixed(1)}%</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-brand-500 rounded-full transition-all duration-500"
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
        <div className="flex justify-between text-xs mt-1.5">
          <span className="text-success-500 font-medium">Repaid: {formatINR(repaid)}</span>
          <span className="text-gray-400">Original: {formatINR(loan.principal_amount)}</span>
        </div>
      </div>

      {/* Additional Info */}
      <div className="flex items-center gap-4 text-xs text-gray-500 mb-4">
        <span className="flex items-center gap-1">
          <Calendar className="w-3.5 h-3.5" />
          EMI due: {loan.emi_due_day}th every month
        </span>
        {loan.total_emis_remaining && (
          <span className="flex items-center gap-1">
            <TrendingDown className="w-3.5 h-3.5" />
            {loan.total_emis_remaining} EMIs left
          </span>
        )}
      </div>

      {loan.loan_manager_phone && (
        <div className="flex items-center gap-1 text-xs text-gray-400 mb-4">
          <Phone className="w-3.5 h-3.5" />
          Manager: {loan.loan_manager_name} — {loan.loan_manager_phone}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={() => onViewSchedule(loan)}
          className="flex-1 py-2 text-sm font-medium border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-gray-700"
        >
          View Schedule
        </button>
        {loan.status === "Active" && (
          <button
            onClick={() => onRecordPayment(loan)}
            className="flex-1 py-2 text-sm font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors"
          >
            Record EMI
          </button>
        )}
      </div>
    </div>
  );
}