import React from "react";
import { HighlightedText } from "./HighlightedText";

interface ReadingModeViewProps {
  paragraphs: string[];
  cleanText: string;
  searchQuery: string;
}

export function ReadingModeView({
  paragraphs,
  cleanText,
  searchQuery,
}: ReadingModeViewProps) {
  // If no paragraphs array, split cleanText by double newlines
  const displayParagraphs =
    paragraphs && paragraphs.length > 0
      ? paragraphs
      : cleanText.split(/\n\n+/).filter(Boolean);

  if (displayParagraphs.length === 0) {
    return (
      <div className="py-12 text-center text-slate-400 text-sm">
        No transcript content available.
      </div>
    );
  }

  return (
    <div className="space-y-6 text-slate-200 text-base sm:text-lg leading-relaxed sm:leading-8 font-normal">
      {displayParagraphs.map((paragraph, index) => (
        <p key={index} className="tracking-normal transition-colors">
          <HighlightedText text={paragraph} searchQuery={searchQuery} />
        </p>
      ))}
    </div>
  );
}
