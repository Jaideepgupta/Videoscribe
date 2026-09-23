"use client";

import React, { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { UploadCloud, FileVideo, AlertCircle, X, CheckCircle2 } from "lucide-react";
import { ProgressBar } from "../ui/progress-bar";
import { uploadVideoFile, ApiError } from "../../services/api";
import { cn } from "../../lib/utils";
import { useToast } from "../ui/toast";

const ALLOWED_EXTENSIONS = [
  ".mp4",
  ".mov",
  ".webm",
  ".mkv",
  ".avi",
  ".mp3",
  ".wav",
  ".m4a",
  ".aac",
  ".ogg",
  ".flac",
];
const MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024; // 500MB

export function FileUploadDropzone() {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const { showToast } = useToast();

  const validateFile = (file: File): string | null => {
    const fileNameLower = file.name.toLowerCase();
    const hasValidExt = ALLOWED_EXTENSIONS.some((ext) => fileNameLower.endsWith(ext));

    if (!hasValidExt) {
      return `Unsupported file format. Supported formats: ${ALLOWED_EXTENSIONS.join(", ")}`;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      return "File is too large. Maximum supported size is 500MB.";
    }

    return null;
  };

  const handleFile = async (file: File) => {
    const error = validateFile(file);
    if (error) {
      setErrorMessage(error);
      return;
    }

    setSelectedFile(file);
    setErrorMessage(null);
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const response = await uploadVideoFile(file, (pct) => {
        setUploadProgress(pct);
      });
      showToast("File uploaded successfully! Processing started.", "info");
      router.push(`/process/${response.job_id}`);
    } catch (err: unknown) {
      setIsUploading(false);
      setSelectedFile(null);
      if (err instanceof ApiError) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Upload failed. Please try again or check your network.");
      }
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const onFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full space-y-4">
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
        className={cn(
          "relative flex flex-col items-center justify-center p-8 sm:p-12 rounded-2xl border-2 border-dashed transition-all duration-200 cursor-pointer text-center",
          "bg-slate-900/40 hover:bg-slate-900/70 backdrop-blur-md",
          isDragging
            ? "border-indigo-500 bg-indigo-950/20 scale-[1.01]"
            : "border-slate-700/80 hover:border-slate-500/80",
          isUploading && "pointer-events-none opacity-90"
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ALLOWED_EXTENSIONS.join(",")}
          onChange={onFileSelect}
          className="hidden"
          disabled={isUploading}
        />

        <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4 shadow-inner">
          <UploadCloud className="w-7 h-7" />
        </div>

        <h3 className="text-base font-semibold text-white mb-1">
          {selectedFile ? selectedFile.name : "Drag & drop your video or audio file here"}
        </h3>
        <p className="text-xs sm:text-sm text-slate-400 mb-3">
          Supports MP4, MOV, WEBM, MKV, MP3, WAV (up to 500MB)
        </p>

        {!isUploading ? (
          <span className="inline-flex items-center px-4 py-2 rounded-xl text-xs font-medium bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700 transition-colors">
            Browse files
          </span>
        ) : (
          <div className="w-full max-w-xs mt-2 space-y-2">
            <ProgressBar value={uploadProgress} showLabel height="sm" color="indigo" />
            <span className="text-xs text-indigo-300 animate-pulse">
              Uploading file... {uploadProgress}%
            </span>
          </div>
        )}
      </div>

      {errorMessage && (
        <div className="p-3.5 rounded-xl bg-rose-950/50 border border-rose-800/50 text-rose-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            className="text-rose-400 hover:text-rose-200 ml-2"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
