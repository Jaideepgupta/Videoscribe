/**
 * TypeScript interface definitions matching backend Pydantic schemas.
 */

export type PlatformType = "youtube" | "vimeo" | "upload" | "direct";

export type JobStatus =
  | "queued"
  | "detecting"
  | "extracting"
  | "transcribing"
  | "cleaning"
  | "completed"
  | "failed";

export interface VideoSubmitRequest {
  url: string;
}

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  error_message?: string | null;
  video_id: string;
  transcript_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TranscriptSegment {
  id: string;
  start_time: number;
  end_time: number;
  duration: number;
  timestamp_label: string;
  text: string;
  speaker?: string | null;
}

export interface TranscriptResponse {
  id: string;
  video_id: string;
  title: string;
  source_url?: string | null;
  platform: PlatformType;
  duration: number;
  duration_formatted: string;
  language: string;
  raw_text: string;
  clean_text: string;
  paragraphs: string[];
  segments: TranscriptSegment[];
  created_at: string;
}

export interface UploadResponse {
  job_id: string;
  status: JobStatus;
  filename: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  redis: string;
}

export interface ApiErrorDetail {
  error?: string;
  message?: string;
  detail?: string | Array<{ msg: string; loc: string[] }>;
}
