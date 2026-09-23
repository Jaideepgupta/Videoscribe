import * as React from "react";
import { cn } from "../../lib/utils";
import { JobStatus, PlatformType } from "../../types/api";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "secondary" | "success" | "danger" | "warning" | "info" | "purple";
  size?: "sm" | "md";
}

export function Badge({
  className,
  variant = "default",
  size = "md",
  children,
  ...props
}: BadgeProps) {
  const variantStyles = {
    default: "bg-slate-800 text-slate-300 border-slate-700/60",
    secondary: "bg-indigo-950/60 text-indigo-300 border-indigo-800/40",
    success: "bg-emerald-950/60 text-emerald-300 border-emerald-800/40",
    danger: "bg-rose-950/60 text-rose-300 border-rose-800/40",
    warning: "bg-amber-950/60 text-amber-300 border-amber-800/40",
    info: "bg-sky-950/60 text-sky-300 border-sky-800/40",
    purple: "bg-purple-950/60 text-purple-300 border-purple-800/40",
  };

  const sizeStyles = {
    sm: "px-2 py-0.5 text-xs font-medium",
    md: "px-2.5 py-1 text-xs font-semibold",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border shadow-sm backdrop-blur-sm",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

export function JobStatusBadge({ status }: { status: JobStatus }) {
  switch (status) {
    case "completed":
      return (
        <Badge variant="success">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          Completed
        </Badge>
      );
    case "failed":
      return (
        <Badge variant="danger">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
          Failed
        </Badge>
      );
    case "queued":
      return (
        <Badge variant="secondary">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
          Queued
        </Badge>
      );
    case "detecting":
    case "extracting":
    case "transcribing":
    case "cleaning":
      return (
        <Badge variant="purple">
          <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-ping" />
          Processing
        </Badge>
      );
    default:
      return <Badge>{status}</Badge>;
  }
}

export function PlatformBadge({ platform }: { platform: PlatformType }) {
  switch (platform) {
    case "youtube":
      return (
        <Badge variant="danger">
          <span className="font-bold">YouTube</span>
        </Badge>
      );
    case "vimeo":
      return (
        <Badge variant="info">
          <span className="font-bold">Vimeo</span>
        </Badge>
      );
    case "upload":
      return (
        <Badge variant="purple">
          <span>Direct Upload</span>
        </Badge>
      );
    case "direct":
      return (
        <Badge variant="secondary">
          <span>Direct Link</span>
        </Badge>
      );
  }
}
