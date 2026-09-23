"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Link2, Sparkles, X, ClipboardPaste } from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { submitVideoUrl, ApiError } from "../../services/api";
import { useToast } from "../ui/toast";

export function UrlInputForm() {
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const router = useRouter();
  const { showToast } = useToast();

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setUrl(text.trim());
        setErrorMessage(null);
      }
    } catch {
      showToast("Unable to access clipboard", "error");
    }
  };

  const handleClear = () => {
    setUrl("");
    setErrorMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanUrl = url.trim();

    if (!cleanUrl) {
      setErrorMessage("Please enter a video URL.");
      return;
    }

    if (!/^https?:\/\//i.test(cleanUrl)) {
      setErrorMessage("Please enter a valid URL starting with http:// or https://");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const result = await submitVideoUrl(cleanUrl);
      showToast("Video queued for processing!", "info");
      router.push(`/process/${result.job_id}`);
    } catch (err: unknown) {
      setIsLoading(false);
      if (err instanceof ApiError) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to submit video. Please check the URL and try again.");
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-3">
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Input
            type="url"
            placeholder="Paste YouTube, Vimeo, or direct video URL..."
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              if (errorMessage) setErrorMessage(null);
            }}
            prefixElement={<Link2 className="w-4 h-4" />}
            suffixElement={
              url ? (
                <button
                  type="button"
                  onClick={handleClear}
                  className="hover:text-white transition-colors p-1"
                  aria-label="Clear input"
                >
                  <X className="w-4 h-4" />
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handlePaste}
                  className="text-xs text-slate-400 hover:text-indigo-300 flex items-center gap-1 px-2 py-1 rounded bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 transition-colors"
                  title="Paste from clipboard"
                >
                  <ClipboardPaste className="w-3.5 h-3.5" />
                  <span>Paste</span>
                </button>
              )
            }
            error={Boolean(errorMessage)}
            disabled={isLoading}
            className="text-base py-3.5"
            autoFocus
          />
        </div>
        <Button
          type="submit"
          size="lg"
          loading={isLoading}
          disabled={isLoading || !url.trim()}
          className="w-full sm:w-auto shrink-0 px-8"
        >
          <Sparkles className="w-4 h-4 mr-1.5" />
          <span>Get Content</span>
        </Button>
      </div>

      {errorMessage && (
        <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-sm flex items-center justify-between animate-in fade-in duration-200">
          <span>{errorMessage}</span>
          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            className="text-rose-400 hover:text-rose-200 ml-2"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </form>
  );
}
