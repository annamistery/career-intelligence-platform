import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import { AnalysisListItem } from '@/types/api';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { ArrowLeft, FileText, Calendar } from 'lucide-react';
import toast from 'react-hot-toast';

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState<AnalysisListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await apiService.listAnalyses();
      setAnalyses(data);
    } catch (error) {
      toast.error('Ошибка загрузки истории');
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
        <h1 className="text-3xl font-bold text-gray-900 mb-8">История анализов</h1>

        {analyses.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <FileText className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <p className="text-xl text-gray-600 mb-4">У вас пока нет анализов</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Создать первый анализ
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {analyses.map((analysis) => (
              <div
                key={analysis.id}
                onClick={() => navigate(`/analysis/${analysis.id}`)}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
              >
                <div className="flex items-start justify-between mb-4">
                  <FileText className="w-10 h-10 text-primary-600" />
                  <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                    Анализ #{analysis.id}
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-gray-600">
                    <Calendar className="w-4 h-4" />
                    <span className="text-sm">
                      {format(new Date(analysis.created_at), 'dd MMMM yyyy, HH:mm', { locale: ru })}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    Карьерных треков: {analysis.career_tracks_count}
                  </p>
                </div>
                <button className="mt-4 w-full py-2 bg-primary-50 text-primary-600 rounded-lg hover:bg-primary-100 transition-colors">
                  Посмотреть результаты
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};
