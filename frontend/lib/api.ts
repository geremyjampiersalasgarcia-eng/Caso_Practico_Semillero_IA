export const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  agents?: string[];
  image?: string;
}

export interface SourceInfo {
  document_name: string;
  content_snippet: string;
  relevance_score?: number;
}

export interface ChatRequest {
  question: string;
  conversation_id?: string;
  image?: string;          // Base64 de imagen para agente multimodal
  confirmation?: boolean;  // Confirmación para agente de acción
}

export interface ChatResponse {
  answer: string;
  meta: {
    agents_used: string[];
    latency_ms: number;
    conversation_id: string;
  };
  sources: SourceInfo[];
  warnings: string[];
}

export interface ConversationListResponse {
  id: string;
  title: string | null;
  updated_at: string;
}

export interface MessageResponse {
  id: number;
  role: "user" | "assistant";
  content: string;
  sources: SourceInfo[];
  agents_used: string[];
  created_at: string;
}

export interface ConversationDetailResponse {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  messages: MessageResponse[];
}

export const api = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  },
  
  async getConversations(): Promise<ConversationListResponse[]> {
    const response = await fetch(`${API_BASE_URL}/conversations/`);
    if (!response.ok) throw new Error("Error loading conversations");
    return response.json();
  },

  async getConversation(id: string): Promise<ConversationDetailResponse> {
    const response = await fetch(`${API_BASE_URL}/conversations/${id}`);
    if (!response.ok) throw new Error("Error loading conversation detail");
    return response.json();
  },

  async deleteConversation(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/conversations/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Error deleting conversation");
  },

  async checkHealth() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  }
};
