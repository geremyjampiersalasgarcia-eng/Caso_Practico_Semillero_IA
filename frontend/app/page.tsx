"use client";

import React, { useEffect, useRef, useState } from "react";
import { Sidebar } from "@/components/chat/Sidebar";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { ChatInput } from "@/components/chat/ChatInput";
import { useChat } from "@/hooks/useChat";
import { Sparkles, Menu } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Home() {
  const { messages, isLoading, sendMessage } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [currentTime, setCurrentTime] = useState<string>("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleString('es-ES', { 
        weekday: 'long', 
        day: 'numeric', 
        month: 'short', 
        hour: '2-digit', 
        minute: '2-digit' 
      }));
    };
    updateTime();
    const interval = setInterval(updateTime, 60000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, isLoading]);

  return (
    <div className="flex h-screen w-full overflow-hidden text-slate-800 bg-background">
      {/* Sidebar Wrapper with animation */}
      <div 
        className={cn(
          "transition-all duration-300 ease-in-out shrink-0 h-full",
          isSidebarOpen ? "w-[280px]" : "w-0 opacity-0 pointer-events-none"
        )}
      >
        <Sidebar />
      </div>
      
      <main className="flex flex-1 flex-col relative">
        {/* Header (Glass) */}
        <header className="absolute top-0 left-0 right-0 z-10 flex h-16 items-center justify-between px-6 glass-panel border-x-0 border-t-0 bg-white/50">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-full hover:bg-slate-100 text-slate-500 transition-colors"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-blue-500" />
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-indigo-500 bg-clip-text text-transparent">
                Mesa de Ayuda IA
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Fecha y Hora */}
            {currentTime && (
              <div className="text-sm text-slate-500 font-medium capitalize hidden md:block">
                {currentTime}
              </div>
            )}
            
            <div className="flex items-center gap-2 text-sm font-medium text-slate-500 bg-white/60 px-3 py-1.5 rounded-full shadow-sm border border-slate-100">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              Conectado al RAG
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto px-4 pt-24 pb-32"
        >
          <div className="mx-auto max-w-4xl space-y-8">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6 animate-in fade-in zoom-in duration-700">
                <div className="h-20 w-20 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-400 flex items-center justify-center shadow-lg shadow-blue-500/30">
                  <Sparkles className="h-10 w-10 text-white" />
                </div>
                <h2 className="text-4xl font-bold tracking-tight text-slate-800">
                  ¿Cómo te puedo ayudar hoy?
                </h2>
                <p className="max-w-xl text-lg text-slate-500 leading-relaxed">
                  Soy tu asistente orquestador potenciado por IA. Consulta sobre normativas, 
                  arquitectura y documentación, y te daré respuestas precisas basadas en el conocimiento interno.
                </p>
              </div>
            ) : (
              messages.map((msg) => (
                <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
              ))
            )}
            
            {isLoading && (
              <div className="flex items-center gap-4 py-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-400 p-[2px] shadow-sm">
                  <div className="h-full w-full bg-white rounded-full flex items-center justify-center">
                    <Sparkles className="h-5 w-5 text-blue-500 animate-pulse" />
                  </div>
                </div>
                <div className="flex space-x-1.5">
                  <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Input Area (Floating) */}
        <div className="absolute bottom-6 left-0 right-0 px-4">
          <div className="mx-auto max-w-4xl relative">
            <ChatInput onSend={sendMessage} isLoading={isLoading} />
            <div className="text-center text-xs text-slate-400 mt-3 font-medium">
              La IA puede cometer errores. Por favor, verifica la información importante.
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
