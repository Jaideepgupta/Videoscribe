import React from "react";

interface HighlightedTextProps {
  text: string;
  searchQuery: string;
  className?: string;
}

export function HighlightedText({
  text,
  searchQuery,
  className,
}: HighlightedTextProps) {
  const cleanQuery = searchQuery.trim();

  if (!cleanQuery || cleanQuery.length < 2) {
    return <span className={className}>{text}</span>;
  }

  try {
    const escapedQuery = cleanQuery.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const parts = text.split(new RegExp(`(${escapedQuery})`, "gi"));

    return (
      <span className={className}>
        {parts.map((part, i) =>
          part.toLowerCase() === cleanQuery.toLowerCase() ? (
            <mark
              key={i}
              className="bg-amber-400/30 text-amber-200 px-1 py-0.5 rounded font-medium shadow-sm shadow-amber-900/30"
            >
              {part}
            </mark>
          ) : (
            <React.Fragment key={i}>{part}</React.Fragment>
          )
        )}
      </span>
    );
  } catch {
    return <span className={className}>{text}</span>;
  }
}
