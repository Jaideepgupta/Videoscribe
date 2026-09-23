"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Sparkles } from "lucide-react";
import { useJobStatus } from "../../../hooks/useJobStatus";
import { StepChecklist } from "../../../components/processing/StepChecklist";
import { ProcessingErrorView } from "../../../components/processing/ProcessingErrorView";
import { ProgressBar } from "../../../components/ui/progress-bar";
import { Card, CardContent } from "../../../components/ui/card";
import { JobStatusBadge } from "../../../components/ui/badge";

export default function ProcessPage({
  params,
}: {
  params: { jobId: string };
}) {
  const router = useRouter();
  const { jobId } = params;
  const { job, isLoading, isCompleted, isFailed, error, refetch } = useJobStatus(
    jobId,
    { pollingIntervalMs: 1500 }
  );

  useEffect(() => {
    if (isCompleted && job) {
      const targetId = job.transcript_id || job.video_id;
      if (targetId) {
        // Brief timeout for smooth UX transition
        const timer = setTimeout(() => {
          router.push(`/transcript/${targetId}`);
        }, 800);
        return () => clearTimeout(timer);
      }
    }
  }, [isCompleted, job, router]);

  const currentStatus = job?.status || "queued";
  const progressPercent = job?.progress || 5;

  return (
    <div className="py-12 sm:py-16 md:py-20 px-4 sm:px-6 max-w-3xl mx-auto">
      <div className="text-center space-y-3 mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Processing Pipeline</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Transcribing Your Video
        </h1>
        <p className="text-sm sm:text-base text-slate-400 max-w-md mx-auto">
          We&apos;re extracting, transcribing, and cleaning your content. This usually takes just a few seconds.
        </p>
      </div>

      <Card className="bg-slate-900/70 border-slate-800/90 shadow-2xl">
        <CardContent className="p-6 sm:p-8 space-y-8">
          {/* Header Progress Bar & Badge */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <JobStatusBadge status={currentStatus} />
                <span className="text-xs text-slate-400 font-mono">Job: {jobId.substring(0, 8)}...</span>
              </div>
              <span className="text-sm font-bold text-indigo-300">{progressPercent}%</span>
            </div>
            <ProgressBar
              value={progressPercent}
              color={isFailed ? "rose" : isCompleted ? "emerald" : "indigo"}
              height="md"
            />
          </div>

          {/* Conditional Error or Step Checklist */}
          {isFailed ? (
            <ProcessingErrorView
              errorMessage={error || "Video processing failed. Please try again."}
              onRetry={refetch}
            />
          ) : (
            <div className="space-y-6">
              <StepChecklist currentStatus={currentStatus} isFailed={isFailed} />
              
              {isCompleted && (
                <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-800/40 text-center space-y-1 animate-in fade-in duration-300">
                  <p className="text-sm font-semibold text-emerald-300">
                    Transcription Complete!
                  </p>
                  <p className="text-xs text-emerald-400/80">
                    Redirecting to your formatted transcript...
                  </p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
