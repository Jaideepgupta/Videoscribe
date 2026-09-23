import React from "react";
import { CheckCircle2, Circle, Loader2, AlertCircle } from "lucide-react";
import { JobStatus } from "../../types/api";
import { cn } from "../../lib/utils";

interface StepItem {
  key: JobStatus;
  label: string;
  description: string;
  order: number;
}

const STEPS: StepItem[] = [
  {
    key: "detecting",
    label: "Video Analysis",
    description: "Detecting video source and retrieving metadata",
    order: 1,
  },
  {
    key: "extracting",
    label: "Caption / Audio Extraction",
    description: "Checking existing captions or extracting audio stream",
    order: 2,
  },
  {
    key: "transcribing",
    label: "Speech Recognition",
    description: "Transcribing spoken content to text",
    order: 3,
  },
  {
    key: "cleaning",
    label: "Text Normalization",
    description: "Cleaning duplicates, formatting paragraphs & aligning timestamps",
    order: 4,
  },
  {
    key: "completed",
    label: "Ready",
    description: "Transcript generated and formatted",
    order: 5,
  },
];

const STATUS_ORDER: Record<JobStatus, number> = {
  queued: 0,
  detecting: 1,
  extracting: 2,
  transcribing: 3,
  cleaning: 4,
  completed: 5,
  failed: -1,
};

export function StepChecklist({
  currentStatus,
  isFailed = false,
}: {
  currentStatus: JobStatus;
  isFailed?: boolean;
}) {
  const currentOrder = STATUS_ORDER[currentStatus] ?? 0;

  return (
    <div className="space-y-4">
      {STEPS.map((step) => {
        const isStepCompleted = !isFailed && currentOrder > step.order;
        const isStepActive = !isFailed && currentOrder === step.order;
        const isStepPending = currentOrder < step.order;
        const isStepFailed = isFailed && currentOrder === step.order;

        return (
          <div
            key={step.key}
            className={cn(
              "flex items-start gap-4 p-4 rounded-xl border transition-all duration-200",
              isStepCompleted && "bg-emerald-950/20 border-emerald-900/40 text-emerald-200",
              isStepActive && "bg-indigo-950/30 border-indigo-700/60 text-white shadow-md shadow-indigo-950/30",
              isStepPending && "bg-slate-900/30 border-slate-800/60 text-slate-500",
              isStepFailed && "bg-rose-950/30 border-rose-900/50 text-rose-300"
            )}
          >
            <div className="mt-0.5 shrink-0">
              {isStepCompleted && <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
              {isStepActive && <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />}
              {isStepPending && <Circle className="w-5 h-5 text-slate-600" />}
              {isStepFailed && <AlertCircle className="w-5 h-5 text-rose-400" />}
            </div>

            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{step.label}</span>
                {isStepActive && (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 animate-pulse">
                    Processing
                  </span>
                )}
                {isStepCompleted && (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    Done
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400">{step.description}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
