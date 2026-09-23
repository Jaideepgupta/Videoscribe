"use client";

import React, { useState, useRef, useEffect } from "react";
import { Copy, Download, Check, FileText, Code2, Sparkles, ChevronDown } from "lucide-react";
import { Button } from "../ui/button";
import { TranscriptResponse } from "../../types/api";
import {
  copyToClipboard,
  downloadTxtFile,
  downloadMarkdownFile,
  downloadJsonFile,
} from "../../utils/export";
import { useToast } from "../ui/toast";

interface TranscriptActionsProps {
  transcript: TranscriptResponse;
}

export function TranscriptActions({ transcript }: TranscriptActionsProps) {
  const [isCopied, setIsCopied] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { showToast } = useToast();

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsExportOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleCopy = async () => {
    const success = await copyToClipboard(transcript.clean_text);
    if (success) {
      setIsCopied(true);
      showToast("Transcript copied to clipboard!", "success");
      setTimeout(() => setIsCopied(false), 2000);
    } else {
      showToast("Failed to copy to clipboard", "error");
    }
  };

  const handleDownloadTxt = () => {
    downloadTxtFile(transcript.title, transcript.clean_text, {
      sourceUrl: transcript.source_url,
      durationFormatted: transcript.duration_formatted,
      language: transcript.language,
    });
    setIsExportOpen(false);
    showToast("Downloaded plain text transcript", "info");
  };

  const handleDownloadMarkdown = () => {
    downloadMarkdownFile(
      transcript.title,
      transcript.clean_text,
      transcript.segments,
      {
        sourceUrl: transcript.source_url,
        durationFormatted: transcript.duration_formatted,
        language: transcript.language,
        platform: transcript.platform,
      }
    );
    setIsExportOpen(false);
    showToast("Downloaded Markdown transcript", "info");
  };

  const handleDownloadJson = () => {
    downloadJsonFile(transcript.title, transcript);
    setIsExportOpen(false);
    showToast("Downloaded JSON transcript data", "info");
  };

  return (
    <div className="flex items-center gap-2.5">
      {/* Copy Button */}
      <Button
        variant="secondary"
        size="md"
        onClick={handleCopy}
        className="font-semibold shadow-sm"
      >
        {isCopied ? (
          <>
            <Check className="w-4 h-4 mr-1.5 text-emerald-400" />
            <span>Copied!</span>
          </>
        ) : (
          <>
            <Copy className="w-4 h-4 mr-1.5 text-indigo-400" />
            <span>Copy All</span>
          </>
        )}
      </Button>

      {/* Export Dropdown */}
      <div className="relative" ref={dropdownRef}>
        <Button
          variant="primary"
          size="md"
          onClick={() => setIsExportOpen((prev) => !prev)}
          className="font-semibold"
        >
          <Download className="w-4 h-4 mr-1.5" />
          <span>Export</span>
          <ChevronDown className="w-3.5 h-3.5 ml-1.5 opacity-70" />
        </Button>

        {isExportOpen && (
          <div className="absolute right-0 mt-2 w-52 rounded-xl bg-slate-900/95 border border-slate-700/80 shadow-2xl backdrop-blur-xl p-1.5 z-40 space-y-1 animate-in fade-in zoom-in-95 duration-150">
            <button
              onClick={handleDownloadTxt}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-medium rounded-lg text-slate-200 hover:text-white hover:bg-slate-800 transition-colors text-left"
            >
              <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
              <div>
                <p className="font-semibold">Plain Text (.txt)</p>
                <p className="text-[10px] text-slate-400">Clean reading text</p>
              </div>
            </button>

            <button
              onClick={handleDownloadMarkdown}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-medium rounded-lg text-slate-200 hover:text-white hover:bg-slate-800 transition-colors text-left"
            >
              <Sparkles className="w-4 h-4 text-violet-400 shrink-0" />
              <div>
                <p className="font-semibold">Markdown (.md)</p>
                <p className="text-[10px] text-slate-400">With timestamps & frontmatter</p>
              </div>
            </button>

            <button
              onClick={handleDownloadJson}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-medium rounded-lg text-slate-200 hover:text-white hover:bg-slate-800 transition-colors text-left"
            >
              <Code2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <div>
                <p className="font-semibold">JSON (.json)</p>
                <p className="text-[10px] text-slate-400">Raw segments & timestamps</p>
              </div>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
