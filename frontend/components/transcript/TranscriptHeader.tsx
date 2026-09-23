import React from "react";
import { Clock, Globe, ExternalLink, Video } from "lucide-react";
import { PlatformBadge, Badge } from "../ui/badge";
import { PlatformType } from "../../types/api";

interface TranscriptHeaderProps {
  title: string;
  platform: PlatformType;
  durationFormatted: string;
  language: string;
  sourceUrl?: string | null;
}

export function TranscriptHeader({
  title,
  platform,
  durationFormatted,
  language,
  sourceUrl,
}: TranscriptHeaderProps) {
  return (
    <div className="space-y-4">
      {/* Title */}
      <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight">
        {title || "Video Transcript"}
      </h1>

      {/* Metadata Badges Bar */}
      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-300">
        <PlatformBadge platform={platform} />

        <Badge variant="default" className="gap-1.5 font-mono">
          <Clock className="w-3.5 h-3.5 text-indigo-400" />
          <span>{durationFormatted || "00:00"}</span>
        </Badge>

        <Badge variant="secondary" className="gap-1.5 uppercase font-medium">
          <Globe className="w-3.5 h-3.5 text-indigo-400" />
          <span>{language || "EN"}</span>
        </Badge>

        {sourceUrl && (
          <a
            href={sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800/80 text-slate-300 border border-slate-700 hover:text-white hover:border-slate-500 transition-colors"
          >
            <Video className="w-3.5 h-3.5 text-indigo-400" />
            <span>Watch Original</span>
            <ExternalLink className="w-3 h-3 opacity-60" />
          </a>
        )}
      </div>
    </div>
  );
}
