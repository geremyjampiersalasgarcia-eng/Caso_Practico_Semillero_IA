import React from "react";
import { cn } from "@/lib/utils";
import { Bot, User } from "lucide-react";
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
        "flex w-full items-start gap-4 py-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border shadow bg-primary text-primary-foreground">
          <Bot className="h-5 w-5" />
        </div>
      )}

      <div
        className={cn(
          "relative flex max-w-[80%] flex-col gap-2 rounded-lg px-4 py-3 text-sm shadow-sm",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted border text-foreground"
        )}
      >
        <div className="prose prose-sm dark:prose-invert max-w-none break-words">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {content}
          </ReactMarkdown>
        </div>
      </div>

      {isUser && (
        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border shadow bg-secondary text-secondary-foreground">
          <User className="h-5 w-5" />
        </div>
      )}
    </div>
  );
}
