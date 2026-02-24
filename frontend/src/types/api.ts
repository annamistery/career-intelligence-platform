// API response types

export interface User {
  id: number;
  email: string;
  full_name?: string;
  date_of_birth?: string;
  gender?: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
  date_of_birth: string;
  gender: string;
}

export interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  extracted_skills?: {
    hard_skills: string[];
    soft_skills: string[];
  };
  uploaded_at: string;
}

// ===== PGD =====

export interface PGDData {
  main_cup: Record<string, number | null>;
  ancestral_data: Record<string, number | null>;
  crossroads: Record<string, number | null>;
  tasks?: Record<string, number | null>;
  business_periods?: {
    [key: string]: Record<string, number | null> | null;
  };
}

// ===== Analysis =====

export interface CareerTrack {
  title: string;
  description: string;
  match_score: number;
  key_strengths: string[];
  development_areas: string[];
}

export interface SkillsBreakdown {
  soft_skills: string[];
  hard_skills: string[];
  soft_skills_score: number;
  hard_skills_score: number;
  balance_ratio: string;
}

// Соответствует backend AnalysisResponse
export interface Analysis {
  id: number;
  pgd_data: PGDData;

  client_name: string;
  client_date_of_birth: string;
  client_gender: string;
  insights: string;
  recommendations: string;
  client_document_id?: number | null;

  skills_breakdown?: SkillsBreakdown | null;
  career_tracks?: CareerTrack[] | null;

  created_at: string;
}

// Если хочешь облегчённый список:
export interface AnalysisListItem {
  id: number;
  client_name: string;
  client_date_of_birth: string;
  client_gender: string;
  created_at: string;
}

// Тело запроса на /analysis/create и /analysis/independent
export interface AnalysisRequest {
  name: string;
  date_of_birth: string;              // "DD.MM.YYYY"
  gender: string;                     // "М" или "Ж"
  client_document_id?: number | null; // обязателен для /create
  include_documents?: boolean;
}

export interface ApiError {
  detail: unknown;
}
