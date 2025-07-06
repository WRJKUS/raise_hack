/**
 * API client for Leonardo's RFQ Alchemy backend
 */

// Use 127.0.0.1 to avoid localhost resolution issues in containers
const API_BASE_URL = `http://127.0.0.1:8000/api`;
console.log('API Base URL:', API_BASE_URL);

export interface Proposal {
  id: string;
  title: string;
  content: string;
  budget: number;
  timeline_months: number;
  category: string;
  created_at: string;
}

export interface AnalysisResult {
  id: string;
  vendor: string;
  fileName: string;
  overallScore: number;
  budgetScore: number;
  technicalScore: number;
  timelineScore: number;
  proposedBudget: string;
  timeline: string;
  contact: string;
  phone: string;
  strengths: string[];
  concerns: string[];
}

export interface ChatMessage {
  id: number;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  message: ChatMessage;
  session_id: string;
  relevant_proposals: string[];
}

export interface AnalysisResponse {
  session_id: string;
  analysis: string;
  proposals_count: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Health check
  async healthCheck(): Promise<{ status: string; message: string }> {
    return this.request('/health');
  }

  // Proposal endpoints
  async uploadProposal(file: File): Promise<{ filename: string; file_id: string; size: number; message: string }> {
    console.log(`API: Starting upload for ${file.name}`);
    console.log(`API: Base URL: ${this.baseUrl}`);
    console.log(`API: Upload URL: ${this.baseUrl}/proposals/upload`);

    const formData = new FormData();
    formData.append('file', file);

    // Add timeout to prevent hanging (reduced for debugging)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      console.log('API: Upload timeout triggered after 15 seconds');
      controller.abort();
    }, 15000); // 15 second timeout for debugging

    try {
      console.log('API: Making fetch request...');
      const startTime = Date.now();

      const response = await fetch(`${this.baseUrl}/proposals/upload`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      const endTime = Date.now();
      clearTimeout(timeoutId);
      console.log(`API: Response received after ${endTime - startTime}ms - Status: ${response.status}, OK: ${response.ok}`);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('API: Upload failed with error data:', errorData);
        throw new Error(errorData.detail || `Upload failed: ${response.status}`);
      }

      const result = await response.json();
      console.log(`API: Upload completed for ${file.name}:`, result);
      return result;
    } catch (error) {
      clearTimeout(timeoutId);
      console.error('API: Upload error:', error);
      console.error('API: Error name:', error.name);
      console.error('API: Error message:', error.message);

      if (error.name === 'AbortError') {
        throw new Error('Upload timeout - please try again');
      }
      throw error;
    }
  }

  async getProposals(): Promise<Proposal[]> {
    return this.request('/proposals/list');
  }

  async getProposal(id: string): Promise<Proposal> {
    return this.request(`/proposals/${id}`);
  }

  async deleteProposal(id: string): Promise<{ message: string }> {
    return this.request(`/proposals/${id}`, { method: 'DELETE' });
  }

  async getAnalysisResults(): Promise<AnalysisResult[]> {
    return this.request('/proposals/analysis/results');
  }

  // Analysis endpoints
  async startAnalysis(sessionId?: string): Promise<AnalysisResponse> {
    return this.request('/analysis/start', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId }),
    });
  }

  async getAnalysisStatus(sessionId: string): Promise<{
    session_id: string;
    started_at: string;
    proposals_count: number;
    analysis_completed: boolean;
    questions_asked: number;
    has_errors: boolean;
    error_message: string;
  }> {
    return this.request(`/analysis/status/${sessionId}`);
  }

  async getAnalysisResult(sessionId: string): Promise<AnalysisResponse> {
    return this.request(`/analysis/result/${sessionId}`);
  }

  // Chat endpoints
  async sendChatMessage(message: string, sessionId?: string): Promise<ChatResponse> {
    return this.request('/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId }),
    });
  }

  async getChatHistory(sessionId: string): Promise<{
    session_id: string;
    messages: ChatMessage[];
  }> {
    return this.request(`/chat/history/${sessionId}`);
  }

  async clearChatSession(sessionId: string): Promise<{ message: string }> {
    return this.request(`/chat/session/${sessionId}`, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
