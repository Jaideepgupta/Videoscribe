"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { getJobStatus, ApiError } from "../services/api";
import { JobResponse } from "../types/api";

interface UseJobStatusOptions {
  pollingIntervalMs?: number;
  maxConsecutiveErrors?: number;
}

interface UseJobStatusReturn {
  job: JobResponse | null;
  isLoading: boolean;
  isCompleted: boolean;
  isFailed: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useJobStatus(
  jobId: string | null,
  options: UseJobStatusOptions = {}
): UseJobStatusReturn {
  const { pollingIntervalMs = 1500, maxConsecutiveErrors = 5 } = options;

  const [job, setJob] = useState<JobResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const errorCountRef = useRef<number>(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef<boolean>(true);

  const isCompleted = job?.status === "completed";
  const isFailed = job?.status === "failed";

  const fetchStatus = useCallback(async () => {
    if (!jobId) return;

    try {
      const data = await getJobStatus(jobId);
      if (!isMountedRef.current) return;

      setJob(data);
      setIsLoading(false);
      errorCountRef.current = 0;

      if (data.status === "failed") {
        setError(data.error_message || "Video processing failed. Please try again.");
      }
    } catch (err: unknown) {
      if (!isMountedRef.current) return;

      errorCountRef.current += 1;
      const apiErr = err instanceof ApiError ? err : null;
      const message =
        apiErr?.message ||
        (err instanceof Error ? err.message : "Failed to fetch job status");

      if (errorCountRef.current >= maxConsecutiveErrors) {
        setIsLoading(false);
        setError(message);
      }
    }
  }, [jobId, maxConsecutiveErrors]);

  useEffect(() => {
    isMountedRef.current = true;
    errorCountRef.current = 0;
    setError(null);
    setIsLoading(true);

    if (!jobId) {
      setIsLoading(false);
      return;
    }

    // Initial fetch
    fetchStatus();

    // Setup polling
    const interval = setInterval(() => {
      // Don't poll if we're done, failed, or hit too many errors
      if (
        job?.status === "completed" ||
        job?.status === "failed" ||
        errorCountRef.current >= maxConsecutiveErrors
      ) {
        return;
      }
      fetchStatus();
    }, pollingIntervalMs);

    timerRef.current = interval;

    return () => {
      isMountedRef.current = false;
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [jobId, job?.status, fetchStatus, pollingIntervalMs, maxConsecutiveErrors]);

  return {
    job,
    isLoading,
    isCompleted,
    isFailed,
    error,
    refetch: fetchStatus,
  };
}
