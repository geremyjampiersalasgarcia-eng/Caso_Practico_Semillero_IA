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

        {/* AI Model Selector / Badge (Gemini Style) */}
        <div className="hidden sm:flex h-10 items-center shrink-0 relative" onClick={(e) => e.stopPropagation()}>
          <button 
            onClick={() => setIsModelMenuOpen(!isModelMenuOpen)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100/80 hover:bg-slate-200/80 text-sm font-semibold text-slate-600 transition-colors mr-2"
          >
            <Sparkles className="h-3.5 w-3.5 text-blue-500" />
            <span>{selectedModel}</span>
            <ChevronDown className={`h-3.5 w-3.5 text-slate-400 transition-transform ${isModelMenuOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Menú Desplegable */}
          {isModelMenuOpen && (
            <div className="absolute bottom-[120%] right-2 w-64 bg-white rounded-2xl shadow-[0_10px_40px_rgb(0,0,0,0.12)] border border-slate-100 p-2 animate-in fade-in zoom-in-95 duration-200 z-50">
              
              <button 
                onClick={() => { setSelectedModel("Orquestador Flash"); setIsModelMenuOpen(false); }}
                className="flex w-full items-start gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors text-left"
              >
                <Zap className="h-5 w-5 mt-0.5 text-emerald-500 shrink-0" />
                <div>
                  <div className="text-sm font-bold text-slate-800">Orquestador Flash</div>
                  <div className="text-xs text-slate-500 mt-0.5">Respuestas rápidas para tareas sencillas.</div>
                </div>
              </button>

              <button 
                onClick={() => { setSelectedModel("Orquestador Pro"); setIsModelMenuOpen(false); }}
                className="flex w-full items-start gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors text-left mt-1"
              >
                <Sparkles className="h-5 w-5 mt-0.5 text-blue-500 shrink-0" />
                <div>
                  <div className="text-sm font-bold text-slate-800">Orquestador Pro</div>
                  <div className="text-xs text-slate-500 mt-0.5">Ayuda completa, programación y análisis profundo.</div>
                </div>
              </button>

              <div className="h-px bg-slate-100 my-1 mx-2"></div>
              
              <button 
                onClick={() => { setSelectedModel("Especialista Avanzado"); setIsModelMenuOpen(false); }}
                className="flex w-full items-start gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors text-left"
              >
                <Brain className="h-5 w-5 mt-0.5 text-purple-500 shrink-0" />
                <div>
                  <div className="text-sm font-bold text-slate-800">Especialista Avanzado</div>
                  <div className="text-xs text-slate-500 mt-0.5">Análisis documental exhaustivo (lento).</div>
                </div>
              </button>

            </div>
          )}
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
