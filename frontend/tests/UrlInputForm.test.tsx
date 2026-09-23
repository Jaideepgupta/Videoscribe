import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";
import { UrlInputForm } from "../components/landing/UrlInputForm";
import { ToastProvider } from "../components/ui/toast";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe("UrlInputForm Component", () => {
  it("renders input field and submit button", () => {
    render(
      <ToastProvider>
        <UrlInputForm />
      </ToastProvider>
    );

    const input = screen.getByPlaceholderText(/Paste YouTube, Vimeo, or direct video URL/i);
    expect(input).toBeInTheDocument();

    const submitBtn = screen.getByRole("button", { name: /Get Content/i });
    expect(submitBtn).toBeInTheDocument();
  });

  it("shows error for invalid scheme URL", async () => {
    render(
      <ToastProvider>
        <UrlInputForm />
      </ToastProvider>
    );

    const input = screen.getByPlaceholderText(/Paste YouTube, Vimeo, or direct video URL/i);
    fireEvent.change(input, { target: { value: "ftp://invalid-url.com/vid" } });

    const submitBtn = screen.getByRole("button", { name: /Get Content/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/Please enter a valid URL starting with http:\/\/ or https:\/\//i)).toBeInTheDocument();
    });
  });
});
