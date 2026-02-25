import React, { useEffect, useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiService } from '@/services/api';
import { AnalysisListItem } from '@/types/api';
import toast from 'react-hot-toast';
import { PlusCircle, Trash2, Eye } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState<AnalysisListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Функция для загрузки списка анализов
  const loadAnalyses = useCallback(async () => {
    try {
      const data = await apiService.listAnalyses();
      setAnalyses(data);
    } catch (error) {
      toast.error('Ошибка загрузки истории анализов');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Загружаем данные при первом рендере
  useEffect(() => {
    setIsLoading(true);
    loadAnalyses();
  }, [loadAnalyses]);

  // Функция для удаления анализа
  const handleDelete = async (id: number) => {
    if (window.confirm('Вы уверены, что хотите удалить этот анализ?')) {
      try {
        await apiService.deleteAnalysis(id);
        toast.success('Анализ успешно удален');
        // Обновляем список после удаления
        setAnalyses(analyses.filter(analysis => analysis.id !== id));
      } catch (error) {
        toast.error('Не удалось удалить анализ');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            История анализов
          </h1>
          {/* 
            ИСПРАВЛЕНО: Вместо формы здесь теперь просто ссылка 
            на новую страницу создания анализа.
          */}
          <Link 
            to="/analysis/new" 
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 shadow-sm"
          >
            <PlusCircle className="w-5 h-5" />
            Создать новый анализ
          </Link>
        </div>

        {isLoading ? (
          <p>Загрузка истории...</p>
        ) : analyses.length > 0 ? (
          <div className="bg-white shadow rounded-lg">
            <ul className="divide-y divide-gray-200">
              {analyses.map(analysis => (
                <li key={analysis.id} className="p-4 flex justify-between items-center">
                  <div>
                    <p className="font-semibold text-gray-800">{analysis.client_name}</p>
                    <p className="text-sm text-gray-500">
                      Создан: {new Date(analysis.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <button
                      onClick={() => navigate(`/analysis/${analysis.id}`)}
                      className="text-primary-600 hover:text-primary-800"
                      title="Просмотреть"
                    >
                      <Eye className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(analysis.id)}
                      className="text-red-500 hover:text-red-700"
                      title="Удалить"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900">История анализов пуста</h3>
            <p className="mt-1 text-sm text-gray-500">Нажмите "Создать новый анализ", чтобы начать.</p>
          </div>
        )}
      </main>
    </div>
  );
};
