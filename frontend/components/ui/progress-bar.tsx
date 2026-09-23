import * as React from "react";
import { cn } from "../../lib/utils";

export interface ProgressBarProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number; // 0 - 100
  showLabel?: boolean;
  color?: "indigo" | "emerald" | "rose" | "amber";
  height?: "sm" | "md" | "lg";
}

export function ProgressBar({
  value,
  showLabel = false,
  color = "indigo",
  height = "md",
  className,
  ...props
}: ProgressBarProps) {
  const clampedValue = Math.min(100, Math.max(0, value));

  const heightClasses = {
    sm: "h-1.5",
    md: "h-2.5",
    lg: "h-4",
  };

  const colorGradients = {
    indigo: "from-indigo-500 via-indigo-600 to-violet-500 shadow-indigo-500/30",
    emerald: "from-emerald-500 via-teal-500 to-emerald-600 shadow-emerald-500/30",
    rose: "from-rose-500 via-red-500 to-pink-600 shadow-rose-500/30",
    amber: "from-amber-500 via-yellow-500 to-amber-600 shadow-amber-500/30",
  };

  return (
    <div className={cn("w-full space-y-1.5", className)} {...props}>
      {showLabel && (
        <div className="flex justify-between text-xs font-medium text-slate-300">
          <span>Progress</span>
          <span>{clampedValue}%</span>
        </div>
      )}
      <div
        className={cn(
          "w-full overflow-hidden rounded-full bg-slate-800/80 border border-slate-700/50 p-0.5",
          heightClasses[height]
        )}
      >
        <div
          className={cn(
            "h-full rounded-full bg-gradient-to-r transition-all duration-500 ease-out shadow-lg",
            colorGradients[color]
          )}
          style={{ width: `${clampedValue}%` }}
        />
      </div>
    </div>
  );
}
