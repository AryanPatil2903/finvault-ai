/**
 * Loans & EMI management page - list, add, view amortization, record payments.
 */

import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { CreditCard, Plus } from "lucide-react";
import LoanCard from "@/components/EMI/LoanCard";
import AmortizationTable from "@/components/EMI/AmortizationTable";
import { useFinanceStore } from "@/store/financeStore";
import { loanApi } from "@/services/api";
import type { AmortizationSchedule, Loan } from "@/types";

export default function Loans() {
  const { loans, fetchLoans } = useFinanceStore();
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedLoan, setSelectedLoan] = useState<Loan | null>(null);
  const [amortization, setAmortization] = useState<AmortizationSchedule | null>(null);
  const [loadingSchedule, setLoadingSchedule] = useState(false);

  // Simple add loan form state
  const [form, setForm] = useState({
    loan_name: "", loan_type: "Personal Loan", lender_name: "",
    principal_amount: "", annual_interest_rate: "", tenure_months: "",
    disbursement_date: "", first_emi_date: "", emi_due_day: "1",
    interest_method: "Reducing Balance", processing_fee: "0",
  });

  useEffect(() => { fetchLoans(); }, [fetchLoans]);

  const handleViewSchedule = async (loan: Loan) => {
    setSelectedLoan(loan);
    setLoadingSchedule(true);
    try {
      const { data } = await loanApi.getAmortization(loan.id);
      setAmortization(data);
    } catch {
      toast.error("Failed to load amortization schedule.");
    } finally {
      setLoadingSchedule(false);
    }
  };

  const handleRecordPayment = async (loan: Loan) => {
    try {
      await loanApi.payNext(loan.id, "UPI");
      toast.success(`EMI recorded for ${loan.loan_name}`);
      fetchLoans();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Could not record EMI.");
    }
  };

  const handleAddLoan = async () => {
    try {
      await loanApi.create({
        ...form,
        principal_amount: parseFloat(form.principal_amount),
        annual_interest_rate: parseFloat(form.annual_interest_rate),
        tenure_months: parseInt(form.tenure_months, 10),
        emi_due_day: parseInt(form.emi_due_day, 10),
        processing_fee: parseFloat(form.processing_fee),
      } as any);
      toast.success("Loan added successfully!");
      setShowAddForm(false);
      fetchLoans();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Failed to add loan.");
    }
  };

  const totalOutstanding = loans.reduce((s, l) => s + l.outstanding_amount, 0);
  const totalEMI = loans
    .filter((l) => l.status === "Active")
    .reduce((s, l) => s + l.emi_amount, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Loans &amp; EMI Tracker</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Total outstanding: &#8377;{totalOutstanding.toLocaleString("en-IN")} &bull;
            Monthly EMI: &#8377;{totalEMI.toLocaleString("en-IN")}
          </p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors text-sm font-medium"
        >
          <Plus className="w-4 h-4" /> Add Loan
        </button>
      </div>

      {/* Loan Cards */}
      {loans.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <CreditCard className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="font-medium">No loans added yet.</p>
          <p className="text-sm">Add your first loan to start tracking EMIs.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {loans.map((loan) => (
            <LoanCard
              key={loan.id}
              loan={loan}
              onViewSchedule={handleViewSchedule}
              onRecordPayment={handleRecordPayment}
            />
          ))}
        </div>
      )}

      {/* Amortization Schedule Modal */}
      {selectedLoan && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  Amortization Schedule &mdash; {selectedLoan.loan_name}
                </h2>
                <p className="text-sm text-gray-500 mt-0.5">
                  {selectedLoan.lender_name} &bull; {selectedLoan.annual_interest_rate}% p.a. &bull;{" "}
                  {selectedLoan.interest_method}
                </p>
              </div>
              <button
                onClick={() => { setSelectedLoan(null); setAmortization(null); }}
                className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
              >
                &times;
              </button>
            </div>
            <div className="overflow-y-auto p-6">
              {loadingSchedule ? (
                <div className="flex items-center justify-center h-40">
                  <div className="animate-spin rounded-full h-8 w-8 border-4 border-brand-500 border-t-transparent" />
                </div>
              ) : amortization ? (
                <AmortizationTable data={amortization} paidCount={selectedLoan.total_emis_paid} />
              ) : null}
            </div>
          </div>
        </div>
      )}

      {/* Add Loan Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold">Add New Loan</h2>
            </div>
            <div className="p-6 space-y-4">
              {[
                { label: "Loan Name", key: "loan_name", type: "text" },
                { label: "Lender / Bank Name", key: "lender_name", type: "text" },
                { label: "Principal Amount (\u20B9)", key: "principal_amount", type: "number" },
                { label: "Annual Interest Rate (%)", key: "annual_interest_rate", type: "number" },
                { label: "Tenure (months)", key: "tenure_months", type: "number" },
                { label: "Disbursement Date", key: "disbursement_date", type: "date" },
                { label: "First EMI Date", key: "first_emi_date", type: "date" },
                { label: "EMI Due Day (1-28)", key: "emi_due_day", type: "number" },
                { label: "Processing Fee (\u20B9)", key: "processing_fee", type: "number" },
              ].map(({ label, key, type }) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                  <input
                    type={type}
                    value={(form as any)[key]}
                    onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none text-sm"
                  />
                </div>
              ))}
            </div>
            <div className="p-6 border-t border-gray-200 flex gap-3">
              <button
                onClick={() => setShowAddForm(false)}
                className="flex-1 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAddLoan}
                className="flex-1 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700"
              >
                Add Loan
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}