/**
 * Root application component — routing, auth guard, layout.
 */

import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Sidebar from "@/components/Layout/Sidebar";
import Dashboard from "@/pages/Dashboard";
import Expenses from "@/pages/Expenses";
import Incomes from "@/pages/Incomes";
import Loans from "@/pages/Loans";
import AIAdvisor from "@/pages/AIAdvisor";
import Login from "@/pages/Login";
import { useAuthStore } from "@/store/authStore";

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-gray-50 font-sans">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-6 lg:p-8">
          {children}
        </div>
      </main>
    </div>
  );
}

function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, fetchMe } = useAuthStore();
  useEffect(() => { if (isAuthenticated) fetchMe(); }, []);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <AuthGuard>
              <ProtectedLayout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/expenses" element={<Expenses />} />
                  <Route path="/incomes" element={<Incomes />} />
                  <Route path="/loans" element={<Loans />} />
                  <Route path="/ai" element={<AIAdvisor />} />
                </Routes>
              </ProtectedLayout>
            </AuthGuard>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}