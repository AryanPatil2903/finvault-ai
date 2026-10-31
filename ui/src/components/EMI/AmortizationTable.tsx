/**
 * Full amortization schedule table with summary stats and row highlighting.
 */

import type { AmortizationSchedule } from "@/types";

interface AmortizationTableProps {
  data: AmortizationSchedule;
  paidCount?: number;   // Highlight paid EMIs
}

function formatINR(n: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency", currency: "INR", maximumFractionDigits: 0,
  }).format(n);
}

export default function AmortizationTable({ data, paidCount = 0 }: AmortizationTableProps) {
  const { summary, schedule } = data;

  return (
    <div>
      {/* Summary Row */}
      <div className="grid grid-cols-4 gap-4 mb-6 p-4 bg-brand-50 rounded-xl border border-brand-100">
        <div>
          <p className="text-xs text-gray-500">Monthly EMI</p>
          <p className="font-bold text-brand-700">{formatINR(summary.emi_amount)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Total Payment</p>
          <p className="font-bold text-gray-900">{formatINR(summary.total_payment)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Total Interest</p>
          <p className="font-bold text-danger-500">{formatINR(summary.total_interest)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Break-even Month</p>
          <p className="font-bold text-gray-900">EMI #{summary.break_even_month}</p>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-gray-200">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {["#", "Due Date", "EMI", "Principal", "Interest", "Outstanding"].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {schedule.map((row) => {
              const isPaid = row.emi_number <= paidCount;
              return (
                <tr
                  key={row.emi_number}
                  className={isPaid ? "bg-success-100/30" : "hover:bg-gray-50 transition-colors"}
                >
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {row.emi_number}
                    {isPaid && <span className="ml-1 text-success-500 text-xs">✓</span>}
                  </td>
                  <td className="px-4 py-3 text-gray-600">
                    {new Date(row.due_date).toLocaleDateString("en-IN", {
                      day: "2-digit", month: "short", year: "numeric",
                    })}
                  </td>
                  <td className="px-4 py-3 font-medium">{formatINR(row.emi_amount)}</td>
                  <td className="px-4 py-3 text-success-600 font-medium">
                    {formatINR(row.principal_component)}
                  </td>
                  <td className="px-4 py-3 text-danger-500">
                    {formatINR(row.interest_component)}
                  </td>
                  <td className="px-4 py-3 text-gray-900">
                    {formatINR(row.outstanding_after)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}