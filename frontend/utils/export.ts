import { TranscriptSegment } from "../types/api";

function sanitizeFilename(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "")
    .substring(0, 60) || "transcript";
}

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

/**
 * Copies text to system clipboard.
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // fallback below
    }
  }

  // Fallback for older browsers or non-secure contexts
  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.style.position = "fixed";
  textArea.style.left = "-999999px";
  textArea.style.top = "-999999px";
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  let successful = false;
  try {
    successful = document.execCommand("copy");
  } catch {
    successful = false;
  }
  document.body.removeChild(textArea);
  return successful;
}

/**
 * Downloads transcript as a clean Plain Text (.txt) file.
 */
export function downloadTxtFile(
  title: string,
  cleanText: string,
  metadata?: {
    sourceUrl?: string | null;
    durationFormatted?: string;
    language?: string;
  }
) {
  const headerLines = [
    `Title: ${title}`,
    metadata?.sourceUrl ? `Source: ${metadata.sourceUrl}` : null,
    metadata?.durationFormatted ? `Duration: ${metadata.durationFormatted}` : null,
    metadata?.language ? `Language: ${metadata.language.toUpperCase()}` : null,
    `Exported: ${new Date().toLocaleString()}`,
    `----------------------------------------`,
    "",
    cleanText,
  ]
    .filter((line) => line !== null)
    .join("\n");

  const blob = new Blob([headerLines], { type: "text/plain;charset=utf-8" });
  const filename = `${sanitizeFilename(title)}.txt`;
  triggerDownload(blob, filename);
}

/**
 * Downloads transcript as structured Markdown (.md) file.
 */
export function downloadMarkdownFile(
  title: string,
  cleanText: string,
  segments: TranscriptSegment[],
  metadata?: {
    sourceUrl?: string | null;
    durationFormatted?: string;
    language?: string;
    platform?: string;
  }
) {
  const mdContent = `---
title: "${title.replace(/"/g, '\\"')}"
platform: "${metadata?.platform || "video"}"
duration: "${metadata?.durationFormatted || "N/A"}"
language: "${metadata?.language || "en"}"
source: "${metadata?.sourceUrl || ""}"
exported_at: "${new Date().toISOString()}"
---

# ${title}

${metadata?.sourceUrl ? `> **Source**: [Watch Video](${metadata.sourceUrl})  ` : ""}
${metadata?.durationFormatted ? `> **Duration**: ${metadata.durationFormatted}  ` : ""}
${metadata?.language ? `> **Language**: ${metadata.language.toUpperCase()}  ` : ""}

---

## 📖 Full Clean Transcript (Reading Mode)

${cleanText}

---

## ⏱️ Timestamped Breakdown

${segments
  .map(
    (seg) =>
      `### [${seg.timestamp_label}]${seg.speaker ? ` **${seg.speaker}**:` : ""}\n\n${seg.text}`
  )
  .join("\n\n")}
`;

  const blob = new Blob([mdContent], { type: "text/markdown;charset=utf-8" });
  const filename = `${sanitizeFilename(title)}.md`;
  triggerDownload(blob, filename);
}

/**
 * Downloads raw JSON payload of transcript and segments.
 */
export function downloadJsonFile(title: string, data: object) {
  const jsonContent = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonContent], { type: "application/json;charset=utf-8" });
  const filename = `${sanitizeFilename(title)}.json`;
  triggerDownload(blob, filename);
}
