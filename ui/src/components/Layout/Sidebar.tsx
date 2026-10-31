/**
 * Collapsible sidebar with navigation links and active state highlighting.
 */

import {
  BarChart3, Bot, CreditCard, DollarSign,
  Home, LogOut, Settings, TrendingDown, TrendingUp, Wallet,
} from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";

const navItems = [
  { to: "/",           icon: Home,         label: "Dashboard"   },
  { to: "/expenses",   icon: TrendingDown,  label: "Expenses"    },
  { to: "/incomes",    icon: TrendingUp,    label: "Income"      },
  { to: "/loans",      icon: CreditCard,    label: "Loans & EMI" },
  { to: "/analytics",  icon: BarChart3,     label: "Analytics"   },
  { to: "/ai",         icon: Bot,           label: "AI Advisor"  },
];

export default function Sidebar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <aside className="flex flex-col w-64 min-h-screen bg-brand-900 text-white">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-white/10">
        <Wallet className="w-8 h-8 text-brand-500" />
        <div>
          <h1 className="font-bold text-lg leading-tight">FinVault AI</h1>
          <p className="text-xs text-white/50">Smart Finance Manager</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-brand-600 text-white"
                  : "text-white/70 hover:bg-white/10 hover:text-white"
              }`
            }
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User + Logout */}
      <div className="px-3 pb-4 border-t border-white/10 pt-4 space-y-2">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center font-semibold text-sm">
            {user?.full_name?.[0]?.toUpperCase() || "U"}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium truncate">{user?.full_name}</p>
            <p className="text-xs text-white/50 truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 w-full rounded-lg text-sm text-white/70 hover:bg-white/10 hover:text-white transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}