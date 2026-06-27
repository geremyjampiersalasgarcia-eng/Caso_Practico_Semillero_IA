import React, { useState, useRef, useEffect } from "react";
import { SendHorizontal, Loader2, Paperclip, ChevronDown, Sparkles, Zap, Brain } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("");
  const [isModelMenuOpen, setIsModelMenuOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState("Orquestador Pro");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        150
      )}px`;
    }
  }, [input]);

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Cierra el menú si haces clic fuera
  useEffect(() => {
    const handleClickOutside = () => setIsModelMenuOpen(false);
    if (isModelMenuOpen) {
      document.addEventListener("click", handleClickOutside);
    }
    return () => document.removeEventListener("click", handleClickOutside);
  }, [isModelMenuOpen]);

  return (
    <div className="relative group shadow-lg shadow-blue-500/10 hover:shadow-blue-500/20 transition-shadow duration-500 rounded-[2rem]">
      
      {/* Animated Gradient Background Wrapper (with overflow hidden just for the border) */}
      <div className="absolute inset-0 rounded-[2rem] overflow-hidden">
        <div className="absolute inset-[-10px] bg-gradient-to-r from-blue-300 via-indigo-400 to-purple-400 bg-[length:200%_200%] animate-bg-pan opacity-70 group-hover:opacity-100 transition-opacity duration-500"></div>
      </div>

      {/* Inner Input Wrapper (needs relative and z-10 so dropdown isn't clipped) */}
      <div className="relative z-10 m-[2px] flex w-full items-end gap-2 rounded-[calc(2rem-2px)] bg-white/95 backdrop-blur-xl px-4 py-3">
        
        {/* Attachment Button */}
        <button className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors">
          <Paperclip className="h-5 w-5" />
        </button>

        {/* Text Area */}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Pregunta sobre la arquitectura, el código..."
          className="max-h-[150px] min-h-[24px] w-full resize-none bg-transparent px-1 py-2 text-[15px] text-slate-700 placeholder:text-slate-400 focus:outline-none disabled:opacity-50 mt-1"
          rows={1}
          disabled={isLoading}
        />

        {/* AI Model Badge */}
        <div className="hidden sm:flex h-10 items-center shrink-0 relative">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100/80 text-sm font-semibold text-slate-600 mr-2 cursor-default border border-slate-200/50">
            <Sparkles className="h-3.5 w-3.5 text-blue-500" />
            <span>Gemini 2.5 Flash</span>
          </div>
        </div>

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full transition-all duration-300 shadow-sm ${
            input.trim() && !isLoading 
              ? "bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md hover:scale-105" 
              : "bg-slate-100 text-slate-300 cursor-not-allowed"
          }`}
        >
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <SendHorizontal className="h-5 w-5 ml-0.5" />
          )}
        </button>
      </div>
    </div>
  );
}
