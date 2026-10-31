import { useEffect } from "react";
import TransactionPage from "@/components/common/TransactionPage";
import { EXPENSE_CATEGORIES } from "@/constants";
import { expenseApi } from "@/services/api";
import { useFinanceStore } from "@/store/financeStore";

export default function Expenses() {
  const { expenses, fetchExpenses } = useFinanceStore();
  useEffect(() => { fetchExpenses(); }, [fetchExpenses]);

  return (
    <TransactionPage
      title="Expenses"
      subtitle="Track every rupee you spend"
      accent="danger"
      categories={EXPENSE_CATEGORIES}
      items={expenses}
      onAdd={async (p) => { await expenseApi.create({ ...p, tags: [], is_recurring: false } as any); await fetchExpenses(); }}
      onDelete={async (id) => { await expenseApi.delete(id); await fetchExpenses(); }}
    />
  );
}