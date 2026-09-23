import {
  JobResponse,
  TranscriptResponse,
  UploadResponse,
  HealthResponse,
  ApiErrorDetail,
} from "../types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  statusCode: number;
  data: ApiErrorDetail | null;

  constructor(message: string, statusCode: number, data: ApiErrorDetail | null = null) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.data = data;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;
    let errorData: ApiErrorDetail | null = null;
    try {
      errorData = await response.json();
      if (errorData?.message) {
        errorMessage = errorData.message;
      } else if (typeof errorData?.detail === "string") {
        errorMessage = errorData.detail;
      } else if (Array.isArray(errorData?.detail) && errorData.detail[0]?.msg) {
        errorMessage = errorData.detail[0].msg;
      }
    } catch {
      // JSON parse failed, use default status text
      if (response.statusText) {
        errorMessage = response.statusText;
      }
    }
    throw new ApiError(errorMessage, response.status, errorData);
  }
  return response.json();
}

/**
 * Submits a public video URL (e.g. YouTube, Vimeo) for transcription.
 */
export async function submitVideoUrl(url: string): Promise<JobResponse> {
  const res = await fetch(`${API_BASE}/api/v1/videos`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url: url.trim() }),
  });
  return handleResponse<JobResponse>(res);
}

/**
 * Uploads a local video/audio file with optional progress tracking.
 */
export function uploadVideoFile(
  file: File,
  onProgress?: (percentage: number) => void
): Promise<UploadResponse> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append("file", file);

    xhr.open("POST", `${API_BASE}/api/v1/uploads`);

    if (xhr.upload && onProgress) {
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percent = Math.round((event.loaded / event.total) * 100);
          onProgress(percent);
        }
      };
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const parsed = JSON.parse(xhr.responseText);
          resolve(parsed);
        } catch {
          reject(new ApiError("Invalid response from server", xhr.status));
        }
      } else {
        let msg = `Upload failed with status ${xhr.status}`;
        try {
          const parsed = JSON.parse(xhr.responseText);
          msg = parsed.message || parsed.detail || msg;
        } catch {
          // ignore
        }
        reject(new ApiError(msg, xhr.status));
      }
    };

    xhr.onerror = () => {
      reject(new ApiError("Network error occurred during file upload", 0));
    };

    xhr.send(formData);
  });
}

/**
 * Fetches the current status and progress of a background job.
 */
export async function getJobStatus(jobId: string): Promise<JobResponse> {
  const res = await fetch(`${API_BASE}/api/v1/jobs/${encodeURIComponent(jobId)}`, {
    method: "GET",
    headers: {
      "Cache-Control": "no-cache",
    },
  });
  return handleResponse<JobResponse>(res);
}

/**
 * Fetches the processed transcript, paragraphs, and timestamps by ID.
 */
export async function getTranscript(transcriptId: string): Promise<TranscriptResponse> {
  const res = await fetch(
    `${API_BASE}/api/v1/transcripts/${encodeURIComponent(transcriptId)}`,
    {
      method: "GET",
    }
  );
  return handleResponse<TranscriptResponse>(res);
}

/**
 * Fetches backend service health status.
 */
export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/api/v1/health`, {
    method: "GET",
  });
  return handleResponse<HealthResponse>(res);
}
