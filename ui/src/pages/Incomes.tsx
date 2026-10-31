import { useEffect } from "react";
import TransactionPage from "@/components/common/TransactionPage";
import { INCOME_CATEGORIES } from "@/constants";
import { incomeApi } from "@/services/api";
import { useFinanceStore } from "@/store/financeStore";

export default function Incomes() {
  const { incomes, fetchIncomes } = useFinanceStore();
  useEffect(() => { fetchIncomes(); }, [fetchIncomes]);

  return (
    <TransactionPage
      title="Income"
      subtitle="Salary, freelance, and every other source"
      accent="success"
      categories={INCOME_CATEGORIES}
      items={incomes}
      onAdd={async (p) => { await incomeApi.create({ ...p, is_taxable: true } as any); await fetchIncomes(); }}
      onDelete={async (id) => { await incomeApi.delete(id); await fetchIncomes(); }}
    />
  );
}