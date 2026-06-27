"use client";

import React, { useEffect, useRef } from "react";
import { Sidebar } from "@/components/chat/Sidebar";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { ChatInput } from "@/components/chat/ChatInput";
import { useChat } from "@/hooks/useChat";

export default function Home() {
  const { messages, isLoading, sendMessage } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll al último mensaje
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, isLoading]);

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
      <Sidebar />
      
      <main className="flex flex-1 flex-col relative">
        {/* Header */}
        <header className="flex h-14 items-center justify-between border-b px-4 lg:px-6">
          <h1 className="text-lg font-semibold tracking-tight">Mesa de Ayuda - Asistente IA</h1>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            {/* Indicador de estado */}
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            Conectado al RAG
          </div>
        </header>

        {/* Chat Area */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-4 lg:p-8"
        >
          <div className="mx-auto max-w-3xl space-y-6 pb-20">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-4 mt-20 text-muted-foreground">
                <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
                  🤖
                </div>
                <h2 className="text-xl font-semibold text-foreground">¿En qué puedo ayudarte hoy?</h2>
                <p className="max-w-md">
                  Soy el agente orquestador. Hago consultas a la base de conocimiento 
                  para darte respuestas precisas sobre las normativas, arquitectura y documentación.
                </p>
              </div>
            ) : (
              messages.map((msg) => (
                <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
              ))
            )}
            
            {isLoading && (
              <div className="flex items-center gap-4 py-4 text-muted-foreground animate-pulse">
                <div className="h-8 w-8 rounded-md bg-muted"></div>
                <div className="h-4 w-32 bg-muted rounded"></div>
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="p-4 bg-background border-t">
          <div className="mx-auto max-w-3xl relative">
            <ChatInput onSend={sendMessage} isLoading={isLoading} />
            <div className="text-center text-xs text-muted-foreground mt-2">
              La IA puede cometer errores. Verifica la información importante en la documentación oficial.
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
