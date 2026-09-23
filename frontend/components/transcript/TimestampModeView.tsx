import React from "react";
import { Play, Copy, Check, ExternalLink } from "lucide-react";
import { TranscriptSegment, PlatformType } from "../../types/api";
import { HighlightedText } from "./HighlightedText";
import { copyToClipboard } from "../../utils/export";
import { useToast } from "../ui/toast";

interface TimestampModeViewProps {
  segments: TranscriptSegment[];
  sourceUrl?: string | null;
  platform?: PlatformType;
  searchQuery: string;
}

export function TimestampModeView({
  segments,
  sourceUrl,
  platform,
  searchQuery,
}: TimestampModeViewProps) {
  const { showToast } = useToast();
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  const getTimestampUrl = (startTime: number): string | null => {
    if (!sourceUrl) return null;
    const seconds = Math.floor(startTime);

    if (platform === "youtube") {
      const url = new URL(sourceUrl);
      url.searchParams.set("t", `${seconds}s`);
      return url.toString();
    } else if (platform === "vimeo") {
      return `${sourceUrl}#t=${seconds}s`;
    }
    return sourceUrl;
  };

  const handleCopySegment = async (id: string, text: string, timestamp: string) => {
    const success = await copyToClipboard(`[${timestamp}] ${text}`);
    if (success) {
      setCopiedId(id);
      showToast("Segment copied to clipboard!", "success");
      setTimeout(() => setCopiedId(null), 2000);
    }
  };

  if (!segments || segments.length === 0) {
    return (
      <div className="py-12 text-center text-slate-400 text-sm">
        No timestamp segments available.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {segments.map((segment) => {
        const timeUrl = getTimestampUrl(segment.start_time);
        const isCopied = copiedId === segment.id;

        return (
          <div
            key={segment.id}
            className="group flex flex-col sm:flex-row items-start sm:items-baseline gap-3 p-4 rounded-xl border border-slate-800/80 bg-slate-900/40 hover:bg-slate-900/80 hover:border-slate-700/80 transition-all duration-200"
          >
            {/* Timestamp Badge / Link */}
            <div className="flex items-center gap-2 shrink-0">
              {timeUrl ? (
                <a
                  href={timeUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-mono font-semibold bg-indigo-950/70 text-indigo-300 border border-indigo-800/60 hover:bg-indigo-900/90 hover:text-white transition-all shadow-inner group-hover:border-indigo-600/70"
                  title="Play video at this timestamp"
                >
                  <Play className="w-3 h-3 fill-current" />
                  <span>{segment.timestamp_label}</span>
                  <ExternalLink className="w-2.5 h-2.5 opacity-60" />
                </a>
              ) : (
                <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-mono font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                  {segment.timestamp_label}
                </span>
              )}

              {segment.speaker && (
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-violet-950/60 text-violet-300 border border-violet-800/40">
                  {segment.speaker}
                </span>
              )}
            </div>

            {/* Segment Content */}
            <div className="flex-1 text-slate-200 text-sm sm:text-base leading-relaxed">
              <HighlightedText text={segment.text} searchQuery={searchQuery} />
            </div>

            {/* Quick Segment Copy Button */}
            <button
              onClick={() =>
                handleCopySegment(segment.id, segment.text, segment.timestamp_label)
              }
              className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all shrink-0 self-start sm:self-auto"
              title="Copy segment text"
            >
              {isCopied ? (
                <Check className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </button>
          </div>
        );
      })}
    </div>
  );
}
