import axios, { AxiosInstance } from 'axios';
import type {
  TokenResponse,
  LoginRequest,
  RegisterRequest,
  Document,
  Analysis,
  AnalysisListItem,
  AnalysisRequest,
} from '@/types/api';

// Явно описываем, что у нас есть VITE_API_URL
const API_BASE_URL =
  (import.meta as ImportMeta & { env: { VITE_API_URL?: string } }).env
    .VITE_API_URL || 'http://localhost:8000';

const API_PREFIX = '/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}${API_PREFIX}`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle token refresh on 401
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config as any;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) {
              throw new Error('No refresh token');
            }

            const { data } = await axios.post<TokenResponse>(
              `${API_BASE_URL}${API_PREFIX}/auth/refresh`,
              { refresh_token: refreshToken }
            );

            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);

            originalRequest.headers = originalRequest.headers || {};
            originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
            return this.client(originalRequest);
          } catch {
            // Refresh failed, logout user
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // ========== Auth ==========

  async register(data: RegisterRequest): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/auth/register', data);
    return response.data;
  }

  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/auth/login', data);
    return response.data;
  }

  // ========== Documents ==========

  async uploadDocument(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<Document>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async listDocuments(): Promise<Document[]> {
    const response = await this.client.get<Document[]>('/documents/');
    return response.data;
  }

  async deleteDocument(id: number): Promise<void> {
    await this.client.delete(`/documents/${id}`);
  }

  // ========== Analysis ==========

  async createAnalysis(request: AnalysisRequest): Promise<Analysis> {
    const response = await this.client.post<Analysis>('/analysis/create', request);
    return response.data;
  }

  async listAnalyses(): Promise<AnalysisListItem[]> {
    const response = await this.client.get<AnalysisListItem[]>('/analysis/');
    return response.data;
  }

  async getAnalysis(id: number): Promise<Analysis> {
    const response = await this.client.get<Analysis>(`/analysis/${id}`);
    return response.data;
  }

  async deleteAnalysis(id: number): Promise<void> {
    await this.client.delete(`/analysis/${id}`);
  }

  async clearAnalyses(): Promise<void> {
    await this.client.delete('/analysis/');
  }

  // Новый метод для независимого анализа по дате рождения + опциональное резюме
  async independentAnalysis(payload: {
    name: string;
    date_of_birth: string;
    gender: string;
    client_document_id?: number | null;
  }): Promise<Analysis> {
    const response = await this.client.post<Analysis>('/analysis/independent', payload);
    return response.data;
  }
}

export const apiService = new ApiService();

const apiService = {
  // ... (ваш существующий метод getAnalysis)
  getAnalysis: async (id: number): Promise<Analysis> => {
    // Ваша текущая реализация
  },
  
  // ### ДОБАВЬТЕ ЭТОТ МЕТОД ###
  /**
   * Создает новый анализ на сервере.
   * @param analysisData - Данные для анализа (соответствуют AnalysisCreateRequest в FastAPI).
   */
  createAnalysis: async (analysisData: {
    name: string;
    date_of_birth: string;
    gender: string;
    include_pgd: boolean;
    include_resume: boolean;
    client_document_id: number | null;
  }): Promise<{ analysis_id: number }> => {
    // Отправляем запрос на новый единый эндпоинт POST /analysis/
    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(analysisData),
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Ошибка создания анализа');
    }
    return response.json();
  },

  // ### И ДОБАВЬТЕ ЭТОТ МЕТОД ###
  /**
   * Получает список документов пользователя.
   */
  getUserDocuments: async (): Promise<{ id: number; filename: string; created_at: string }[]> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/documents/`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
    });
    if (!response.ok) {
        throw new Error('Ошибка загрузки документов');
    }
    return response.json();
  },
  
  // ... (остальные ваши методы)
};

export { apiService };
