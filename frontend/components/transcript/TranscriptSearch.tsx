"use client";

import React from "react";
import { Search, ChevronUp, ChevronDown, X } from "lucide-react";
import { Input } from "../ui/input";
import { cn } from "../../lib/utils";

interface TranscriptSearchProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  totalMatches: number;
  activeMatchIndex: number;
  onNextMatch: () => void;
  onPrevMatch: () => void;
  onClear: () => void;
  className?: string;
}

export function TranscriptSearch({
  searchQuery,
  onSearchChange,
  totalMatches,
  activeMatchIndex,
  onNextMatch,
  onPrevMatch,
  onClear,
  className,
}: TranscriptSearchProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (e.shiftKey) {
        onPrevMatch();
      } else {
        onNextMatch();
      }
    } else if (e.key === "Escape") {
      onClear();
    }
  };

  return (
    <div className={cn("relative flex items-center gap-2", className)}>
      <div className="relative flex-1">
        <Input
          type="text"
          placeholder="Search spoken words in transcript... (Press Enter to cycle)"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          onKeyDown={handleKeyDown}
          prefixElement={<Search className="w-4 h-4" />}
          suffixElement={
            searchQuery ? (
              <div className="flex items-center gap-1.5">
                {totalMatches > 0 && (
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-indigo-950/80 text-indigo-300 border border-indigo-800/60">
                    {activeMatchIndex + 1}/{totalMatches}
                  </span>
                )}
                {searchQuery && totalMatches === 0 && (
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">
                    0 matches
                  </span>
                )}
                <button
                  type="button"
                  onClick={onClear}
                  className="hover:text-white transition-colors p-1"
                  aria-label="Clear search"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : null
          }
          className="text-sm py-2 bg-slate-900/90 border-slate-800"
        />
      </div>

      {totalMatches > 0 && (
        <div className="flex items-center gap-1 shrink-0 bg-slate-900 border border-slate-800 rounded-xl p-1">
          <button
            type="button"
            onClick={onPrevMatch}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title="Previous match (Shift + Enter)"
          >
            <ChevronUp className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={onNextMatch}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title="Next match (Enter)"
          >
            <ChevronDown className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
