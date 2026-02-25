import axios, { AxiosInstance } from 'axios';
// Убедитесь, что импортируете все нужные типы
import type {
  TokenResponse,
  LoginRequest,
  RegisterRequest,
  Document, // Предполагается, что у вас есть этот тип
  Analysis,
  AnalysisListItem,
} from '@/types/api';

const API_BASE_URL = (import.meta as ImportMeta & { env: { VITE_API_URL?: string } }).env.VITE_API_URL || 'http://localhost:8000';
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

    // Перехватчик для добавления токена авторизации
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Перехватчик для обработки 401 ошибки и обновления токена
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config as any;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) throw new Error('No refresh token');
            
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
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // ========== Auth (без изменений) ==========
  async register(data: RegisterRequest): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/auth/register', data);
    return response.data;
  }

  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/auth/login', data);
    return response.data;
  }

  // ========== Documents (метод переименован) ==========
  async uploadDocument(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post<Document>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  // ПЕРЕИМЕНОВАНО: listDocuments -> getUserDocuments для соответствия с формой
  async getUserDocuments(): Promise<Document[]> {
    const response = await this.client.get<Document[]>('/documents/');
    return response.data;
  }

  async deleteDocument(id: number): Promise<void> {
    await this.client.delete(`/documents/${id}`);
  }

  // ========== Analysis (методы обновлены) ==========

  /**
   * Создает новый анализ на сервере, используя единый эндпоинт.
   * @param analysisData Данные для анализа, соответствующие AnalysisCreateRequest в FastAPI.
   */
  async createAnalysis(analysisData: {
    name: string;
    date_of_birth: string;
    gender: string;
    include_pgd: boolean;
    include_resume: boolean;
    client_document_id: number | null;
  }): Promise<{ analysis_id: number }> {
    // УДАЛЕНЫ старые методы /create и /independent.
    // ИСПОЛЬЗУЕТСЯ новый единый эндпоинт /analysis/
    const response = await this.client.post<{ analysis_id: number }>('/analysis/', analysisData);
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
}

// Экспортируем единственный экземпляр нашего сервиса
export const apiService = new ApiService();
