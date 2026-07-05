import { useState, useCallback } from "react";
import { api, ChatMessage } from "@/lib/api";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (
    content: string,
    image?: string,
    confirmation?: boolean,
  ) => {
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
        question: content,
        conversation_id: conversationId,
        image,
        confirmation,
      });

      // Guardar el conversation_id para futuras llamadas
      if (res.meta.conversation_id) {
        setConversationId(res.meta.conversation_id);
      }

      // Construir contenido del mensaje con warnings si existen
      let botContent = res.answer;
      if (res.warnings && res.warnings.length > 0) {
        botContent += "\n\n⚠️ **Advertencias:** " + res.warnings.join(", ");
      }

      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: botContent,
        sources: res.sources.map(s => s.document_name),
        agents: res.meta.agents_used,
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

  const loadConversation = useCallback(async (id: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const detail = await api.getConversation(id);
      setConversationId(detail.id);
      
      const loadedMessages: ChatMessage[] = detail.messages.map(m => ({
        id: m.id.toString(),
        role: m.role,
        content: m.content,
        sources: m.sources ? m.sources.map(s => s.document_name) : [],
        agents: m.agents_used || [],
      }));
      setMessages(loadedMessages);
    } catch (err: any) {
      setError(err.message || "Error al cargar la conversación");
    } finally {
      setIsLoading(false);
    }
  }, []);

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
    loadConversation,
  };
}
