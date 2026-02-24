import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import { AnalysisListItem } from '@/types/api';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { ArrowLeft, FileText, Calendar, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState<AnalysisListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

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

  useEffect(() => {
    loadHistory();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить этот анализ?')) return;
    try {
      await apiService.deleteAnalysis(id);
      setAnalyses(prev => prev.filter(a => a.id !== id));
      toast.success('Анализ удалён');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка удаления');
    }
  };

  const handleClearHistory = async () => {
    if (!confirm('Точно очистить всю историю анализов?')) return;
    try {
      await apiService.clearAnalyses();
      setAnalyses([]);
      toast.success('История очищена');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка очистки истории');
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
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex items-center justify-between">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-5 h-5" />
            Назад к дашборду
          </button>

          {analyses.length > 0 && (
            <button
              onClick={handleClearHistory}
              className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 border border-red-200 rounded-lg hover:bg-red-50"
            >
              <Trash2 className="w-4 h-4" />
              Очистить историю
            </button>
          )}
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
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div
                  onClick={() => navigate(`/analysis/${analysis.id}`)}
                  className="cursor-pointer"
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
                        {format(new Date(analysis.created_at), 'dd MMMM yyyy, HH:mm', {
                          locale: ru,
                        })}
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

                <button
                  onClick={() => handleDelete(analysis.id)}
                  className="mt-3 w-full py-2 text-sm text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors flex items-center justify-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Удалить анализ
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};
