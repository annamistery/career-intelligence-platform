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

export interface PGDData {
  main_cup: Record<string, number | null>;
  ancestral_data: Record<string, number | null>;
  crossroads: Record<string, number | null>;
  tasks?: Record<string, number | null>;
  business_periods?: {
    business_periods: Record<string, number | null>;
  };
}

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

export interface Analysis {
  id: number;
  pgd_data: PGDData;
  ai_analysis: string;
  career_tracks: CareerTrack[];
  skills_breakdown: SkillsBreakdown;
  created_at: string;
}

export interface AnalysisListItem {
  id: number;
  created_at: string;
  career_tracks_count: number;
}

export interface AnalysisRequest {
  include_documents: boolean;
}

export interface ApiError {
  detail: string;
}
