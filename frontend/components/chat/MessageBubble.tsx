import React from "react";
import { cn } from "@/lib/utils";
import { User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
}

export function MessageBubble({ role, content }: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div
      className={cn(
        "flex w-full items-start gap-5 py-2 animate-in fade-in slide-in-from-bottom-2 duration-500",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex h-10 w-10 shrink-0 select-none items-center justify-center rounded-full bg-white shadow-sm mt-1 overflow-hidden">
          <img src="/logo.png" alt="Logo" className="h-7 w-7 object-contain" />
        </div>
      )}

      <div
        className={cn(
          "relative flex max-w-[85%] flex-col gap-2 px-6 py-4 text-[15px] shadow-sm leading-relaxed",
          isUser
            ? "bg-slate-100/80 border border-slate-200/50 text-slate-800 rounded-3xl rounded-tr-sm"
            : "bg-white border border-slate-100 text-slate-700 rounded-3xl rounded-tl-sm shadow-[0_4px_20px_rgb(0,0,0,0.03)]"
        )}
      >
        <div className="prose prose-slate max-w-none break-words prose-p:leading-relaxed prose-pre:bg-slate-50 prose-pre:border prose-pre:border-slate-100 prose-pre:text-slate-700 prose-headings:font-bold">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {content}
          </ReactMarkdown>
        </div>
      </div>

      {isUser && (
        <div className="flex h-10 w-10 shrink-0 select-none items-center justify-center rounded-full bg-slate-100 border border-slate-200 text-slate-600 shadow-sm mt-1">
          <User className="h-5 w-5" />
        </div>
      )}
    </div>
  );
}
