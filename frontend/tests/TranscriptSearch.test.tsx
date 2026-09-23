import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import { TranscriptSearch } from "../components/transcript/TranscriptSearch";

describe("TranscriptSearch Component", () => {
  it("renders search input correctly", () => {
    const onSearchChange = vi.fn();
    render(
      <TranscriptSearch
        searchQuery=""
        onSearchChange={onSearchChange}
        totalMatches={0}
        activeMatchIndex={0}
        onNextMatch={vi.fn()}
        onPrevMatch={vi.fn()}
        onClear={vi.fn()}
      />
    );

    const input = screen.getByPlaceholderText(/Search spoken words in transcript/i);
    expect(input).toBeInTheDocument();
  });

  it("displays match count when matches are present", () => {
    render(
      <TranscriptSearch
        searchQuery="snowflake"
        onSearchChange={vi.fn()}
        totalMatches={5}
        activeMatchIndex={1}
        onNextMatch={vi.fn()}
        onPrevMatch={vi.fn()}
        onClear={vi.fn()}
      />
    );

    expect(screen.getByText("2/5")).toBeInTheDocument();
  });
});
