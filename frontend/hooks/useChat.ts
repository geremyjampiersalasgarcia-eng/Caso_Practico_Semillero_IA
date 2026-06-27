import { useState, useCallback } from "react";
import { api, ChatMessage } from "@/lib/api";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    // Add user message to UI immediately
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content,
    };
    
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    setError(null);

    try {
      const res = await api.sendMessage({
        query: content,
        conversation_id: conversationId,
      });

      // Guardar el conversation_id para futuras llamadas
      if (res.conversation_id) {
        setConversationId(res.conversation_id);
      }

      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: res.answer,
        sources: res.sources,
        agents: res.agents,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      setError(err.message || "Ocurrió un error de red");
      // Optionally add an error message to the chat
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "❌ Lo siento, ocurrió un error al procesar tu solicitud.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setConversationId(undefined);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
  };
}
