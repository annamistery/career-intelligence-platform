import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import { Analysis } from '@/types/api';
import { ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { ArrowLeft, Download, TrendingUp } from 'lucide-react';
import toast from 'react-hot-toast';

export const AnalysisPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadAnalysis = useCallback(async () => {
    if (!id) {
      setIsLoading(false);
      return;
    }
    try {
      const data = await apiService.getAnalysis(Number(id));
      setAnalysis(data);
    } catch (error) {
      toast.error('Ошибка загрузки анализа');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    setIsLoading(true);
    loadAnalysis();
  }, [loadAnalysis]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Загрузка...</div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Анализ не найден</div>
      </div>
    );
  }

  const hasSkills =
    !!analysis.skills_breakdown &&
    typeof analysis.skills_breakdown.soft_skills_score === 'number' &&
    typeof analysis.skills_breakdown.hard_skills_score === 'number';

  const hasCareerTracks = Array.isArray(analysis.career_tracks) && analysis.career_tracks.length > 0;

  const skillsData = hasSkills
    ? [
        { name: 'Soft Skills', value: analysis.skills_breakdown!.soft_skills_score, fill: '#0ea5e9' },
        { name: 'Hard Skills', value: analysis.skills_breakdown!.hard_skills_score, fill: '#10b981' },
      ]
    : [];

  // ### НАЧАЛО ИСПРАВЛЕНИЯ ###
  // Блок, который исправляет ошибку с "Unterminated regular expression"
  // и динамически убирает приветствие.

  const rawText = analysis.insights || '';
  let cleanedAnalysisText = rawText;

  // 1. Динамически убираем приветствие, используя имя из анализа
  if (analysis.client_name) {
    const greetingToRemove = `Здравствуйте, ${analysis.client_name}.`;
    // Используем .replace() с обычной СТРОКОЙ, а НЕ с регулярным выражением
    cleanedAnalysisText = cleanedAnalysisText.replace(greetingToRemove, '');
  }

  // 2. Убираем остальные ненужные фразы
  cleanedAnalysisText = cleanedAnalysisText
    .replace(
      'Я ваш карьерный консультант и очень рад помочь вам в достижении профессиональных успехов!.',
      '',
    )
    .trim();
  // ### КОНЕЦ ИСПРАВЛЕНИЯ ###

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-5 h-5" />
            Назад к дашборду
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Результаты карьерного анализа
              </h1>
              {analysis.client_name && (
                <p className="text-gray-500 mt-1">
                  Клиент: {analysis.client_name} ({analysis.client_date_of_birth}, {analysis.client_gender})
                </p>
              )}
            </div>
            <button
              onClick={() => {
                const element = document.createElement('a');
                const file = new Blob([cleanedAnalysisText || rawText], { type: 'text/plain;charset=utf-8' });
                element.href = URL.createObjectURL(file);
                element.download = `career-analysis-${id}.txt`;
                document.body.appendChild(element);
                element.click();
                element.remove();
              }}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              <Download className="w-4 h-4" />
              Скачать отчет
            </button>
          </div>

          {hasSkills && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* ... JSX для баланса навыков ... */}
            </div>
          )}

          {hasCareerTracks && (
            <div className="mb-8">
              {/* ... JSX для карьерных треков ... */}
            </div>
          )}

          <div>
            <h2 className="text-2xl font-semibold mb-4">Полный анализ</h2>
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap bg-gray-50 p-6 rounded-lg text-gray-700">
                {cleanedAnalysisText || 'Текст анализа недоступен.'}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
