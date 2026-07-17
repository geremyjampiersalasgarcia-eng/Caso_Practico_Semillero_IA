import React, { useState, useRef, useEffect } from "react";
import { SendHorizontal, Loader2, Paperclip, Sparkles, X, Image } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string, image?: string, confirmation?: boolean) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("");
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [confirmation, setConfirmation] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    if ((input.trim() || imageBase64) && !isLoading) {
      onSend(input.trim() || "Analiza esta imagen", imageBase64 || undefined, confirmation);
      setInput("");
      setImagePreview(null);
      setImageBase64(null);
      setConfirmation(false);
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

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validar que sea imagen
    if (!file.type.startsWith("image/")) {
      alert("Solo se permiten archivos de imagen");
      return;
    }

    // Crear preview
    const reader = new FileReader();
    reader.onload = (event) => {
      const base64 = event.target?.result as string;
      setImagePreview(base64);
      setImageBase64(base64);
    };
    reader.readAsDataURL(file);

    // Limpiar el input para permitir seleccionar el mismo archivo
    e.target.value = "";
  };

  const removeImage = () => {
    setImagePreview(null);
    setImageBase64(null);
  };

  return (
    <div className="relative group shadow-lg shadow-blue-500/10 hover:shadow-blue-500/20 transition-shadow duration-500 rounded-[2rem]">
      
      {/* Animated Gradient Background Wrapper */}
      <div className="absolute inset-0 rounded-[2rem] overflow-hidden">
        <div className="absolute inset-[-10px] bg-gradient-to-r from-blue-300 via-indigo-400 to-purple-400 bg-[length:200%_200%] animate-bg-pan opacity-70 group-hover:opacity-100 transition-opacity duration-500"></div>
      </div>

      {/* Inner Input Wrapper */}
      <div className="relative z-10 m-[2px] flex flex-col w-full rounded-[calc(2rem-2px)] bg-white/95 backdrop-blur-xl">
        
        {/* Image Preview */}
        {imagePreview && (
          <div className="px-4 pt-3 pb-1">
            <div className="relative inline-block">
              <img
                src={imagePreview}
                alt="Preview"
                className="h-20 w-20 object-cover rounded-xl border border-slate-200 shadow-sm"
              />
              <button
                onClick={removeImage}
                className="absolute -top-2 -right-2 h-6 w-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors shadow-sm"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        )}

        <div className="flex items-end gap-2 px-4 py-3">
          {/* Attachment Button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
            title="Adjuntar imagen para análisis multimodal"
          >
            <Image className="h-5 w-5" />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />

          {/* Text Area */}
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Pregunta sobre productos, precios, políticas, CRM..."
            className="max-h-[150px] min-h-[24px] w-full resize-none bg-transparent px-1 py-2 text-[15px] text-slate-700 placeholder:text-slate-400 focus:outline-none disabled:opacity-50 mt-1"
            rows={1}
            disabled={isLoading}
          />

          {/* Confirmation Checkbox */}
          <div className="hidden sm:flex h-10 items-center shrink-0">
            <label className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50/80 text-sm font-medium text-slate-600 mr-2 border border-slate-200/50 cursor-pointer hover:bg-slate-100 transition-colors">
              <input
                type="checkbox"
                checked={confirmation}
                onChange={(e) => setConfirmation(e.target.checked)}
                className="w-3.5 h-3.5 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="whitespace-nowrap">Confirmar</span>
            </label>
          </div>

          {/* AI Model Badge */}
          <div className="hidden sm:flex h-10 items-center shrink-0 relative">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100/80 text-sm font-semibold text-slate-600 mr-2 cursor-default border border-slate-200/50">
              <Sparkles className="h-3.5 w-3.5 text-blue-500" />
              <span>Gemini Flash Lite</span>
            </div>
          </div>

          {/* Send Button */}
          <button
            onClick={handleSend}
            disabled={isLoading || (!input.trim() && !imageBase64)}
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full transition-all duration-300 shadow-sm ${
              (input.trim() || imageBase64) && !isLoading 
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
    </div>
  );
}
