export const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  agents?: string[];
}

export interface SourceInfo {
  document_name: string;
  content_snippet: string;
  relevance_score?: number;
}

export interface ChatRequest {
  question: string;
  conversation_id?: string;
}

export interface ChatResponse {
  answer: string;
  meta: {
    agents_used: string[];
    latency_ms: number;
    conversation_id: string;
  };
  sources: SourceInfo[];
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
  
  async checkHealth() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  }
};
