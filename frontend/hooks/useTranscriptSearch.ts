"use client";

import { useState, useMemo, useCallback } from "react";

export function useTranscriptSearch(text: string) {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [activeMatchIndex, setActiveMatchIndex] = useState<number>(0);

  const cleanQuery = searchQuery.trim();

  // Find all match occurrences
  const totalMatches = useMemo(() => {
    if (!cleanQuery || cleanQuery.length < 2) return 0;
    try {
      const regex = new RegExp(cleanQuery.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
      const matches = text.match(regex);
      return matches ? matches.length : 0;
    } catch {
      return 0;
    }
  }, [cleanQuery, text]);

  const nextMatch = useCallback(() => {
    if (totalMatches > 0) {
      setActiveMatchIndex((prev) => (prev + 1) % totalMatches);
    }
  }, [totalMatches]);

  const prevMatch = useCallback(() => {
    if (totalMatches > 0) {
      setActiveMatchIndex((prev) => (prev - 1 + totalMatches) % totalMatches);
    }
  }, [totalMatches]);

  const handleQueryChange = useCallback((newQuery: string) => {
    setSearchQuery(newQuery);
    setActiveMatchIndex(0);
  }, []);

  const clearSearch = useCallback(() => {
    setSearchQuery("");
    setActiveMatchIndex(0);
  }, []);

  return {
    searchQuery,
    setSearchQuery: handleQueryChange,
    totalMatches,
    activeMatchIndex,
    nextMatch,
    prevMatch,
    clearSearch,
  };
}
