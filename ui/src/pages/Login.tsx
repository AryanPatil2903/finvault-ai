/**
 * Login and Registration page with tab switching.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Wallet } from "lucide-react";
import toast from "react-hot-toast";
import { useAuthStore } from "@/store/authStore";

export default function Login() {
  const [tab, setTab] = useState<"login" | "register">("login");
  const [form, setForm] = useState({
    full_name: "", email: "", password: "",
    monthly_income: "0",
  });
  const { login, register, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async () => {
    try {
      if (tab === "login") {
        await login(form.email, form.password);
      } else {
        await register({
          full_name: form.full_name,
          email: form.email,
          password: form.password,
          monthly_income: parseFloat(form.monthly_income) || 0,
        });
        await login(form.email, form.password);
      }
      toast.success("Welcome to FinVault AI!");
      navigate("/");
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Authentication failed.");
    }
  };

  const F = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-900 via-brand-800 to-brand-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <Wallet className="w-10 h-10 text-brand-300" />
          <div className="text-white">
            <h1 className="text-3xl font-bold">FinVault AI</h1>
            <p className="text-brand-300 text-sm">Smart Finance & EMI Manager</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b border-gray-200">
            {(["login", "register"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`flex-1 py-4 text-sm font-semibold capitalize transition-colors ${
                  tab === t
                    ? "border-b-2 border-brand-600 text-brand-600"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                {t === "login" ? "Sign In" : "Create Account"}
              </button>
            ))}
          </div>

          <div className="p-8 space-y-4">
            {tab === "register" && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  <input type="text" value={form.full_name} onChange={F("full_name")}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500 outline-none"
                    placeholder="Rahul Sharma" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Monthly Income (₹)</label>
                  <input type="number" value={form.monthly_income} onChange={F("monthly_income")}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500 outline-none"
                    placeholder="75000" />
                </div>
              </>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input type="email" value={form.email} onChange={F("email")}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500 outline-none"
                placeholder="you@example.com" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input type="password" value={form.password} onChange={F("password")}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500 outline-none"
                placeholder="Min 8 characters" />
            </div>
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className="w-full py-3 bg-brand-600 text-white rounded-lg font-semibold hover:bg-brand-700 disabled:opacity-50 transition-colors mt-2"
            >
              {isLoading ? "Loading..." : tab === "login" ? "Sign In" : "Create Account"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}