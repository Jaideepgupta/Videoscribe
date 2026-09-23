"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  FileText,
  Clock,
  ArrowLeft,
  Loader2,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { getTranscript, ApiError } from "../../../services/api";
import { TranscriptResponse } from "../../../types/api";
import { TranscriptHeader } from "../../../components/transcript/TranscriptHeader";
import { TranscriptActions } from "../../../components/transcript/TranscriptActions";
import { TranscriptSearch } from "../../../components/transcript/TranscriptSearch";
import { ReadingModeView } from "../../../components/transcript/ReadingModeView";
import { TimestampModeView } from "../../../components/transcript/TimestampModeView";
import { Tabs } from "../../../components/ui/tabs";
import { Card, CardContent } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { useTranscriptSearch } from "../../../hooks/useTranscriptSearch";

export default function TranscriptPage({
  params,
}: {
  params: { id: string };
}) {
  const { id } = params;
  const [transcript, setTranscript] = useState<TranscriptResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"reading" | "timestamps">("reading");

  const fullTextToSearch = transcript?.clean_text || "";
  const {
    searchQuery,
    setSearchQuery,
    totalMatches,
    activeMatchIndex,
    nextMatch,
    prevMatch,
    clearSearch,
  } = useTranscriptSearch(fullTextToSearch);

  const fetchTranscriptData = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await getTranscript(id);
      setTranscript(data);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to load transcript. Please check the URL or try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTranscriptData();
  }, [id]);

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-20 text-center space-y-4">
        <Loader2 className="w-10 h-10 animate-spin text-indigo-400 mx-auto" />
        <h2 className="text-xl font-semibold text-white">Loading transcript...</h2>
        <p className="text-sm text-slate-400">Formatting paragraphs and timestamp markers</p>
      </div>
    );
  }

  if (errorMessage || !transcript) {
    return (
      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-20 text-center space-y-6">
        <div className="w-14 h-14 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mx-auto">
          <AlertCircle className="w-7 h-7" />
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-white">Transcript Not Found</h2>
          <p className="text-sm text-rose-200">{errorMessage || "Unable to retrieve this transcript."}</p>
        </div>
        <div className="flex items-center justify-center gap-3">
          <Button variant="secondary" onClick={fetchTranscriptData}>
            <RefreshCw className="w-4 h-4 mr-1.5" />
            Retry
          </Button>
          <Link href="/">
            <Button variant="primary">
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              Return to Home
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 sm:py-12 space-y-8">
      {/* Top Back Navigation & Status */}
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </Link>
      </div>

      {/* Header Info */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
          <TranscriptHeader
            title={transcript.title}
            platform={transcript.platform}
            durationFormatted={transcript.duration_formatted}
            language={transcript.language}
            sourceUrl={transcript.source_url}
          />

          <div className="shrink-0">
            <TranscriptActions transcript={transcript} />
          </div>
        </div>

        {/* Search and Mode Toolbar */}
        <div className="pt-4 border-t border-slate-800/80 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
          <Tabs
            activeTab={viewMode}
            onChange={(tab) => setViewMode(tab as "reading" | "timestamps")}
            size="md"
            items={[
              {
                id: "reading",
                label: "Reading Mode",
                icon: <FileText className="w-4 h-4" />,
              },
              {
                id: "timestamps",
                label: "Timestamp Mode",
                icon: <Clock className="w-4 h-4" />,
                badge: (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                    {transcript.segments?.length || 0}
                  </span>
                ),
              },
            ]}
          />

          <div className="w-full md:w-80">
            <TranscriptSearch
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              totalMatches={totalMatches}
              activeMatchIndex={activeMatchIndex}
              onNextMatch={nextMatch}
              onPrevMatch={prevMatch}
              onClear={clearSearch}
            />
          </div>
        </div>
      </div>

      {/* Main Transcript Content Card */}
      <Card className="bg-slate-900/60 border-slate-800/90 shadow-2xl">
        <CardContent className="p-6 sm:p-10">
          {viewMode === "reading" ? (
            <ReadingModeView
              paragraphs={transcript.paragraphs}
              cleanText={transcript.clean_text}
              searchQuery={searchQuery}
            />
          ) : (
            <TimestampModeView
              segments={transcript.segments}
              sourceUrl={transcript.source_url}
              platform={transcript.platform}
              searchQuery={searchQuery}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
