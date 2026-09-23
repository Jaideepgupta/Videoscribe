"use client";

import React, { useState } from "react";
import { Link2, UploadCloud, Zap, ShieldCheck, FileText, CheckCircle2, Sparkles, Clock, Search } from "lucide-react";
import { UrlInputForm } from "../components/landing/UrlInputForm";
import { FileUploadDropzone } from "../components/landing/FileUploadDropzone";
import { Card, CardContent } from "../components/ui/card";
import { Tabs } from "../components/ui/tabs";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<string>("url");

  return (
    <div className="relative overflow-hidden py-12 sm:py-16 md:py-20">
      {/* Background Decorative Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-indigo-500/10 blur-[120px] rounded-full pointer-events-none -z-10" />

      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        {/* Hero Header */}
        <div className="text-center space-y-4 mb-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Video & Audio → Clean Readable Text</span>
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white">
            Turn Videos Into{" "}
            <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
              Clean Text
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Extract the complete spoken content from YouTube, Vimeo, or video files.
            Cleaned into cohesive paragraphs without filler noise or broken lines.
          </p>
        </div>

        {/* Ingestion Panel Card */}
        <Card className="border-slate-800/90 shadow-2xl shadow-indigo-950/20 bg-slate-900/70">
          <CardContent className="p-6 sm:p-8 space-y-6">
            {/* Mode Switcher Tabs */}
            <div className="flex justify-center">
              <Tabs
                activeTab={activeTab}
                onChange={setActiveTab}
                items={[
                  {
                    id: "url",
                    label: "Paste Video Link",
                    icon: <Link2 className="w-4 h-4" />,
                  },
                  {
                    id: "upload",
                    label: "Upload Video File",
                    icon: <UploadCloud className="w-4 h-4" />,
                  },
                ]}
              />
            </div>

            {/* Input Form Views */}
            {activeTab === "url" ? (
              <div className="space-y-4">
                <UrlInputForm />
                <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-slate-400 pt-2">
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> YouTube & Shorts
                  </span>
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Vimeo
                  </span>
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Direct MP4 / WebM
                  </span>
                </div>
              </div>
            ) : (
              <FileUploadDropzone />
            )}
          </CardContent>
        </Card>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mt-14">
          <div className="glass-panel p-5 rounded-2xl space-y-2">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-3">
              <Zap className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-sm">Instant Caption Extraction</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Prioritizes existing video transcripts for instant delivery with zero STT latency.
            </p>
          </div>

          <div className="glass-panel p-5 rounded-2xl space-y-2">
            <div className="w-9 h-9 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400 mb-3">
              <FileText className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-sm">Smart Text Cleaning</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Deduplicates overlapping fragments and formats broken subtitles into fluent paragraphs.
            </p>
          </div>

          <div className="glass-panel p-5 rounded-2xl space-y-2">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-3">
              <Search className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-sm">Search & Timestamp Mode</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Search spoken words with instant highlight navigation or browse timestamped segments.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
