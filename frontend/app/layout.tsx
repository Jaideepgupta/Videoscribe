import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { ToastProvider } from "../components/ui/toast";

export const metadata: Metadata = {
  title: "Video2Content - Turn Videos Into Clean Readable Text",
  description: "Paste a video link or upload a video file to get clean, structured spoken content instantly.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased selection:bg-indigo-500/30 selection:text-indigo-200">
        <ToastProvider>
          <header className="border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-md sticky top-0 z-50">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
              <Link href="/" className="flex items-center gap-3 group transition-transform active:scale-95">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/25 group-hover:shadow-indigo-500/40 transition-shadow">
                  V2C
                </div>
                <span className="font-semibold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent group-hover:from-white group-hover:to-white transition-colors">
                  Video2Content
                </span>
              </Link>
              <nav className="flex items-center gap-4 text-sm text-slate-400">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-950/80 text-indigo-300 border border-indigo-800/50 shadow-inner">
                  v0.1.0 MVP
                </span>
              </nav>
            </div>
          </header>
          <main className="min-h-[calc(100vh-4rem)]">
            {children}
          </main>
        </ToastProvider>
      </body>
    </html>
  );
}

