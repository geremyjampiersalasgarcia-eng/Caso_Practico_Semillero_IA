"use client";

import React, { useEffect, useRef, useState } from "react";
import { Sidebar } from "@/components/chat/Sidebar";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { ChatInput } from "@/components/chat/ChatInput";
import { useChat } from "@/hooks/useChat";
import { Menu } from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";

export default function Home() {
  const { messages, isLoading, sendMessage, clearChat, loadConversation, conversationId } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [currentTime, setCurrentTime] = useState<string>("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [history, setHistory] = useState<{id: string, title: string}[]>([]);

  // Función para refrescar el historial desde el backend
  const refreshHistory = async () => {
    try {
      const data = await api.getConversations();
      setHistory(data.map((c: any) => ({
        id: c.id,
        title: c.title || "Nueva conversación"
      })));
    } catch (error) {
      console.error("Failed to load history", error);
    }
  };

  // Cargar historial inicial y cuando cambie el conversationId (al crear uno nuevo)
  useEffect(() => {
    refreshHistory();
  }, [conversationId]);

  // Función para manejar el botón de Nuevo Chat
  const handleNewChat = () => {
    clearChat();
    refreshHistory();
  };

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
        <Sidebar onNewChat={handleNewChat} onLoadChat={loadConversation} history={history} setHistory={setHistory} />
      </div>
      
      <main className="flex flex-1 flex-col relative bg-gradient-to-b from-blue-300/80 via-blue-200/50 to-blue-50/30">
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
              <img src="/logo.png" alt="Logo" className="h-6 w-6 object-contain" />
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-indigo-500 bg-clip-text text-transparent">
                Patito — Ventas
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
                <div className="h-20 w-20 rounded-full bg-white flex items-center justify-center shadow-lg shadow-blue-500/10 overflow-hidden">
                  <img src="/logo.png" alt="Logo" className="h-16 w-16 object-contain" />
                </div>
                <h2 className="text-4xl font-bold tracking-tight text-slate-800">
                  Mesa de Ayuda — Ventas
                </h2>
                {/* Input Area (Centrado en el medio cuando está vacío) */}
                <div className="w-full max-w-4xl mt-8">
                  <ChatInput onSend={(msg, img, conf) => sendMessage(msg, img, conf)} isLoading={isLoading} />
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
              ))
            )}
            
            {isLoading && (
              <div className="flex items-center gap-4 py-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="h-10 w-10 rounded-full bg-white p-1 shadow-sm overflow-hidden flex items-center justify-center">
                  <img src="/logo.png" alt="Logo" className="h-7 w-7 object-contain animate-pulse" />
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

        {/* Input Area (Fijo en la parte inferior cuando ya hay mensajes) */}
        {messages.length > 0 && (
          <div className="absolute bottom-0 left-0 right-0">
            {/* Gradient fade from blue to transparent going upward */}
            <div className="absolute inset-0 bg-gradient-to-t from-blue-50/80 via-blue-50/40 to-transparent pointer-events-none" />
            <div className="relative px-4 pt-8 pb-6">
              <div className="mx-auto max-w-4xl relative">
                <ChatInput onSend={(msg, img, conf) => sendMessage(msg, img, conf)} isLoading={isLoading} />
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
