import * as React from "react";
import { cn } from "../../lib/utils";

export interface TabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
}

export interface TabsProps {
  items: TabItem[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
  size?: "sm" | "md";
}

export function Tabs({
  items,
  activeTab,
  onChange,
  className,
  size = "md",
}: TabsProps) {
  const sizeStyles = {
    sm: "p-1 text-xs gap-1",
    md: "p-1.5 text-sm gap-1.5",
  };

  const itemSizeStyles = {
    sm: "px-3 py-1 text-xs gap-1.5",
    md: "px-4 py-2 text-sm gap-2",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-md shadow-inner",
        sizeStyles[size],
        className
      )}
      role="tablist"
    >
      {items.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(tab.id)}
            className={cn(
              "inline-flex items-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500",
              itemSizeStyles[size],
              isActive
                ? "bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/20 font-semibold"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            )}
          >
            {tab.icon && <span className="shrink-0">{tab.icon}</span>}
            <span>{tab.label}</span>
            {tab.badge && <span className="ml-1 shrink-0">{tab.badge}</span>}
          </button>
        );
      })}
    </div>
  );
}
