/**
 * Generic add/list/delete page shared by Expenses and Incomes.
 */

import { useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import toast from "react-hot-toast";

interface Item {
  id: string;
  amount: number;
  category: string;
  description?: string;
  transaction_date: string;
}

export interface NewTransaction {
  amount: number;
  category: string;
  description: string;
  transaction_date: string;
}

interface Props {
  title: string;
  subtitle: string;
  accent: "danger" | "success";
  categories: string[];
  items: Item[];
  onAdd: (payload: NewTransaction) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

const inr = (n: number) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);

export default function TransactionPage({ title, subtitle, accent, categories, items, onAdd, onDelete }: Props) {
  const today = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({ amount: "", category: categories[0], description: "", transaction_date: today });
  const total = items.reduce((s, i) => s + i.amount, 0);

  const submit = async () => {
    const amount = parseFloat(form.amount);
    if (!amount || amount <= 0) return toast.error("Enter a valid amount.");
    try {
      await onAdd({ ...form, amount });
      setForm((f) => ({ ...f, amount: "", description: "" }));
      toast.success("Saved.");
    } catch (e: any) {
      toast.error(e.response?.data?.detail?.[0]?.msg || e.response?.data?.detail || "Failed to save.");
    }
  };

  const remove = async (id: string) => {
    try { await onDelete(id); toast.success("Deleted."); }
    catch { toast.error("Failed to delete."); }
  };

  const field = "px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-brand-500";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
        <p className="text-sm text-gray-500 mt-0.5">{subtitle} • Total shown: <b>{inr(total)}</b></p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-4 grid grid-cols-1 md:grid-cols-5 gap-3">
        <input className={field} type="number" placeholder="Amount (₹)" value={form.amount}
          onChange={(e) => setForm({ ...form, amount: e.target.value })} />
        <select className={field} value={form.category}
          onChange={(e) => setForm({ ...form, category: e.target.value })}>
          {categories.map((c) => <option key={c}>{c}</option>)}
        </select>
        <input className={field} type="date" value={form.transaction_date}
          onChange={(e) => setForm({ ...form, transaction_date: e.target.value })} />
        <input className={field} placeholder="Description" value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <button onClick={submit}
          className="flex items-center justify-center gap-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700">
          <Plus className="w-4 h-4" /> Add
        </button>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-600">
            <tr>{["Date", "Category", "Description", "Amount", ""].map((h) => <th key={h} className="px-4 py-3 text-left">{h}</th>)}</tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {items.length === 0 && (
              <tr><td colSpan={5} className="px-4 py-10 text-center text-gray-400">Nothing recorded yet.</td></tr>
            )}
            {items.map((i) => (
              <tr key={i.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-600">{new Date(i.transaction_date).toLocaleDateString("en-IN")}</td>
                <td className="px-4 py-3">{i.category}</td>
                <td className="px-4 py-3 text-gray-500">{i.description || "—"}</td>
                <td className={`px-4 py-3 font-semibold ${accent === "danger" ? "text-danger-500" : "text-success-600"}`}>{inr(i.amount)}</td>
                <td className="px-4 py-3 text-right">
                  <button onClick={() => remove(i.id)} className="text-gray-400 hover:text-danger-500">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}