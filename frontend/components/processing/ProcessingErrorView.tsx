import React from "react";
import Link from "next/link";
import { AlertCircle, RefreshCw, Upload, ArrowLeft } from "lucide-react";
import { Button } from "../ui/button";

interface ProcessingErrorViewProps {
  errorMessage: string;
  onRetry?: () => void;
}

export function ProcessingErrorView({
  errorMessage,
  onRetry,
}: ProcessingErrorViewProps) {
  return (
    <div className="p-6 sm:p-8 rounded-2xl bg-rose-950/20 border border-rose-800/40 text-center space-y-6">
      <div className="w-14 h-14 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mx-auto">
        <AlertCircle className="w-7 h-7" />
      </div>

      <div className="space-y-2 max-w-md mx-auto">
        <h3 className="text-lg font-semibold text-white">
          Processing Encountered an Issue
        </h3>
        <p className="text-sm text-rose-200 leading-relaxed">
          {errorMessage}
        </p>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
        {onRetry && (
          <Button variant="secondary" size="md" onClick={onRetry}>
            <RefreshCw className="w-4 h-4 mr-1.5" />
            Try Again
          </Button>
        )}

        <Link href="/?tab=upload">
          <Button variant="primary" size="md">
            <Upload className="w-4 h-4 mr-1.5" />
            Upload File Instead
          </Button>
        </Link>

        <Link href="/">
          <Button variant="ghost" size="md">
            <ArrowLeft className="w-4 h-4 mr-1.5" />
            Back to Home
          </Button>
        </Link>
      </div>
    </div>
  );
}
