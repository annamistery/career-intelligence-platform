import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import { Analysis } from '@/types/api';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { ArrowLeft, Download, TrendingUp } from 'lucide-react';
import toast from 'react-hot-toast';

export const AnalysisPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAnalysis();
  }, [id]);

  const loadAnalysis = async () => {
    try {
      const data = await apiService.getAnalysis(Number(id));
      setAnalysis(data);
    } catch (error) {
      toast.error('Ошибка загрузки анализа');
    } finally {
      setIsLoading(false);
    }
  };

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

  // Prepare skills chart data
  const skillsData = [
    { name: 'Soft Skills', value: analysis.skills_breakdown.soft_skills_score, fill: '#0ea5e9' },
    { name: 'Hard Skills', value: analysis.skills_breakdown.hard_skills_score, fill: '#10b981' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
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

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">
              Результаты карьерного анализа
            </h1>
            <button
              onClick={() => {
                const element = document.createElement('a');
                const file = new Blob([analysis.ai_analysis], { type: 'text/plain' });
                element.href = URL.createObjectURL(file);
                element.download = `career-analysis-${id}.txt`;
                document.body.appendChild(element);
                element.click();
              }}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              <Download className="w-4 h-4" />
              Скачать отчет
            </button>
          </div>

          {/* Skills Balance */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <div>
              <h2 className="text-xl font-semibold mb-4">Баланс навыков</h2>
              <div className="flex justify-center">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={skillsData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name}: ${entry.value.toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {skillsData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <p className="text-center text-lg font-medium mt-4">
                Соотношение: {analysis.skills_breakdown.balance_ratio}
              </p>
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4">Ваши навыки</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium text-gray-700 mb-2">Soft Skills:</h3>
                  <div className="flex flex-wrap gap-2">
                    {analysis.skills_breakdown.soft_skills.slice(0, 10).map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="font-medium text-gray-700 mb-2">Hard Skills:</h3>
                  <div className="flex flex-wrap gap-2">
                    {analysis.skills_breakdown.hard_skills.slice(0, 10).map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Career Tracks */}
          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-primary-600" />
              Рекомендуемые карьерные треки
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {analysis.career_tracks.map((track, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-lg font-semibold text-gray-900">{track.title}</h3>
                    <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                      {track.match_score}%
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mb-4">{track.description}</p>
                  <div className="mb-3">
                    <h4 className="text-sm font-medium text-gray-700 mb-1">Ваши сильные стороны:</h4>
                    <ul className="list-disc list-inside text-sm text-gray-600">
                      {track.key_strengths.slice(0, 3).map((strength, i) => (
                        <li key={i}>{strength}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-1">Развивать:</h4>
                    <ul className="list-disc list-inside text-sm text-gray-600">
                      {track.development_areas.slice(0, 3).map((area, i) => (
                        <li key={i}>{area}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Analysis */}
          <div>
            <h2 className="text-2xl font-semibold mb-4">Полный анализ</h2>
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap bg-gray-50 p-6 rounded-lg text-gray-700">
                {analysis.ai_analysis}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
