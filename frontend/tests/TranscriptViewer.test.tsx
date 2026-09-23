import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import { ReadingModeView } from "../components/transcript/ReadingModeView";
import { HighlightedText } from "../components/transcript/HighlightedText";

describe("ReadingModeView & HighlightedText", () => {
  it("renders clean paragraphs without timestamps", () => {
    const paragraphs = [
      "Welcome to the masterclass on database indexing.",
      "B-trees and LSM-trees have distinct read-write trade-offs.",
    ];

    render(
      <ReadingModeView
        paragraphs={paragraphs}
        cleanText={paragraphs.join("\n\n")}
        searchQuery=""
      />
    );

    expect(screen.getByText(/Welcome to the masterclass on database indexing/i)).toBeInTheDocument();
    expect(screen.getByText(/B-trees and LSM-trees have distinct read-write trade-offs/i)).toBeInTheDocument();
  });

  it("highlights search term with mark tag", () => {
    const { container } = render(
      <HighlightedText
        text="The quick brown fox jumps over the lazy dog"
        searchQuery="brown"
      />
    );

    const mark = container.querySelector("mark");
    expect(mark).toBeInTheDocument();
    expect(mark?.textContent).toBe("brown");
  });
});
