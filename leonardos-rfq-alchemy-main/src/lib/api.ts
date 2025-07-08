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

// RFP Optimization interfaces
export interface RFPDimensionAnalysis {
  score: number;
  max_score: number;
  findings: string[];
  recommendations: string[];
}

export interface RFPTimelineAnalysis extends RFPDimensionAnalysis {
  timeline_assessment_score: number;
  recommended_timeline_adjustments: string[];
  risk_factors: string[];
  historical_comparison: string[];
}

export interface RFPRequirementsAnalysis extends RFPDimensionAnalysis {
  clarity_score: number;
  requirement_gaps: string[];
  suggested_clarifications: string[];
  deliverable_alignment: string;
}

export interface RFPCostStructureAnalysis extends RFPDimensionAnalysis {
  cost_structure_assessment: string;
  change_management_readiness: string;
  missing_cost_categories: string[];
  recommended_contingencies: string[];
}

export interface RFPTCOAnalysis extends RFPDimensionAnalysis {
  tco_completeness_score: number;
  missing_cost_elements: string[];
  lifecycle_cost_projections: string[];
  budget_realism_check: string;
}

export interface RFPOptimizationAnalysis {
  analysis_id: string;
  rfp_document_id: string;
  analysis_timestamp: string;
  overall_score: number;
  max_score: number;
  timeline_feasibility: RFPTimelineAnalysis;
  requirements_clarity: RFPRequirementsAnalysis;
  cost_flexibility: RFPCostStructureAnalysis;
  tco_analysis: RFPTCOAnalysis;
  priority_actions: string[];
  implementation_timeline: {
    immediate: string[];
    short_term: string[];
    long_term: string[];
  };
  executive_summary: string;
}

export interface RFPOptimizationResponse {
  analysis: RFPOptimizationAnalysis;
  session_id: string;
  processing_time_seconds: number;
}

export interface RFPActionItem {
  id: string;
  title: string;
  description: string;
  priority: 'immediate' | 'short_term' | 'long_term';
  dimension: string;
  completed: boolean;
  created_at: string;
  completed_at?: string;
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

  async getAnalysisResults(sessionId?: string): Promise<AnalysisResult[]> {
    const url = sessionId
      ? `/proposals/analysis/results?session_id=${encodeURIComponent(sessionId)}`
      : '/proposals/analysis/results';
    return this.request(url);
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

  // RFP Optimization endpoints
  async uploadRFPDocument(file: File): Promise<{
    rfp_document_id: string;
    filename: string;
    title: string;
    file_size: number;
    message: string;
  }> {
    console.log(`API: Starting RFP upload for ${file.name}`);

    const formData = new FormData();
    formData.append('file', file);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      console.log('API: RFP upload timeout triggered after 30 seconds');
      controller.abort();
    }, 30000); // 30 second timeout for RFP uploads

    try {
      console.log('API: Making RFP upload request...');
      const startTime = Date.now();

      const response = await fetch(`${this.baseUrl}/rfp-optimization/upload-rfp`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      const endTime = Date.now();
      clearTimeout(timeoutId);
      console.log(`API: RFP upload response received after ${endTime - startTime}ms - Status: ${response.status}`);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('API: RFP upload failed with error data:', errorData);
        throw new Error(errorData.detail || `RFP upload failed: ${response.status}`);
      }

      const result = await response.json();
      console.log(`API: RFP upload completed for ${file.name}:`, result);
      return result;
    } catch (error) {
      clearTimeout(timeoutId);
      console.error('API: RFP upload error:', error);

      if (error.name === 'AbortError') {
        throw new Error('RFP upload timeout - please try again');
      }
      throw error;
    }
  }

  async analyzeRFPDocument(rfpDocumentId: string, sessionId?: string): Promise<RFPOptimizationResponse> {
    return this.request('/rfp-optimization/analyze', {
      method: 'POST',
      body: JSON.stringify({
        rfp_document_id: rfpDocumentId,
        session_id: sessionId,
        include_historical_data: true
      }),
    });
  }

  async getRFPAnalysis(sessionId: string): Promise<RFPOptimizationResponse> {
    return this.request(`/rfp-optimization/analysis/${sessionId}`);
  }

  async getRFPOptimizationSessions(): Promise<{
    sessions: Array<{
      session_id: string;
      rfp_document_id: string;
      created_at: string;
      overall_score: number;
      max_score: number;
      executive_summary: string;
    }>;
    total_count: number;
  }> {
    return this.request('/rfp-optimization/sessions');
  }

  async getRFPActionItems(sessionId: string): Promise<{
    session_id: string;
    action_items: {
      immediate: RFPActionItem[];
      short_term: RFPActionItem[];
      long_term: RFPActionItem[];
    };
    total_count: number;
    completed_count: number;
  }> {
    return this.request(`/rfp-optimization/action-items/${sessionId}`);
  }

  async updateRFPActionItem(sessionId: string, itemId: string, completed: boolean): Promise<{
    message: string;
    item_id: string;
    completed: boolean;
  }> {
    return this.request(`/rfp-optimization/action-items/${sessionId}/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify({ completed, notes: null }),
    });
  }

  async getRFPOptimizationHealth(): Promise<{
    status: string;
    agent_status: string;
    active_sessions: number;
    total_action_items: number;
    timestamp: string;
  }> {
    return this.request('/rfp-optimization/health');
  }
}

export const apiClient = new ApiClient();
