/**
 * Reusable metric card with icon, trend indicator, and formatted value.
 */

import { LucideIcon, TrendingDown, TrendingUp } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: LucideIcon;
  iconColor?: string;
  iconBg?: string;
  trend?: number;          // Positive = good, negative = bad
  trendLabel?: string;
}

export default function StatsCard({
  title, value, subtitle, icon: Icon,
  iconColor = "text-brand-600",
  iconBg = "bg-brand-100",
  trend,
  trendLabel,
}: StatsCardProps) {
  const isPositiveTrend = trend !== undefined && trend >= 0;

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900 truncate">{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-400 mt-0.5">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 rounded-xl ${iconBg} ml-4 flex-shrink-0`}>
          <Icon className={`w-6 h-6 ${iconColor}`} />
        </div>
      </div>

      {trend !== undefined && (
        <div className={`flex items-center gap-1 mt-3 text-xs font-medium
          ${isPositiveTrend ? "text-success-500" : "text-danger-500"}`}>
          {isPositiveTrend
            ? <TrendingUp className="w-3.5 h-3.5" />
            : <TrendingDown className="w-3.5 h-3.5" />
          }
          <span>{Math.abs(trend).toFixed(1)}% {trendLabel || "vs last month"}</span>
        </div>
      )}
    </div>
  );
}