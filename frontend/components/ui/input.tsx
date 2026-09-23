import * as React from "react";
import { cn } from "../../lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
  prefixElement?: React.ReactNode;
  suffixElement?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    { className, type = "text", error = false, prefixElement, suffixElement, ...props },
    ref
  ) => {
    return (
      <div className="relative flex items-center w-full group">
        {prefixElement && (
          <div className="absolute left-3.5 flex items-center pointer-events-none text-slate-400 group-focus-within:text-indigo-400 transition-colors">
            {prefixElement}
          </div>
        )}
        <input
          type={type}
          ref={ref}
          className={cn(
            "w-full bg-slate-900/70 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 shadow-inner backdrop-blur-sm transition-all duration-200",
            "focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-900/90",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            prefixElement ? "pl-11" : "",
            suffixElement ? "pr-11" : "",
            error
              ? "border-rose-500/80 focus:border-rose-500 focus:ring-rose-500/20 text-rose-100"
              : "",
            className
          )}
          {...props}
        />
        {suffixElement && (
          <div className="absolute right-3.5 flex items-center text-slate-400">
            {suffixElement}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";
