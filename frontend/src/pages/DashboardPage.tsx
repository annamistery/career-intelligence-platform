import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { apiService } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';
import toast from 'react-hot-toast';
import { Upload, FileText, Sparkles, LogOut, BarChart3, BrainCircuit, FileSignature } from 'lucide-react';
import axios from 'axios';
import { Document } from '@/types/api'; // Убедитесь, что тип Document импортирован

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // ИСПРАВЛЕНО: Типизируем uploadedFile
  const [uploadedFile, setUploadedFile] = useState<Document | null>(null);

  // НОВОЕ: State для чекбоксов выбора типа анализа
  const [includePgd, setIncludePgd] = useState(true);
  const [includeResume, setIncludeResume] = useState(false);


  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const document = await apiService.uploadDocument(file);
      setUploadedFile(document);
      toast.success('Файл успешно загружен!');
      // НОВОЕ: Автоматически включаем анализ по резюме после успешной загрузки
      setIncludeResume(true); 
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка загрузки');
    } finally {
      setIsUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
  });

  // ИСПРАВЛЕНО: Полностью переписанная функция
  const handleStartAnalysis = async () => {
    if (!user) {
      toast.error('Пользователь не найден. Пожалуйста, перезайдите.');
      return;
    }
    if (includeResume && !uploadedFile) {
      toast.error('Для анализа по резюме сначала загрузите файл.');
      return;
    }
    if (!includePgd && !includeResume) {
      toast.error('Выберите хотя бы один источник данных для анализа.');
      return;
    }

    const name = user.full_name || user.email;
    const date_of_birth = user.date_of_birth || '';
    const gender = user.gender || '';

    if (!date_of_birth || !gender) {
        toast.error('Пожалуйста, заполните дату рождения и пол в вашем профиле.');
        return;
    }

    setIsAnalyzing(true);
    const loadingToast = toast.loading('Создаем анализ... Это может занять до минуты.');

    try {
      // ИСПРАВЛЕНО: Формируем правильный payload
      const payload = {
        name,
        date_of_birth,
        gender,
        include_pgd: includePgd,
        include_resume: includeResume,
        client_document_id: includeResume && uploadedFile ? uploadedFile.id : null,
      };

      const result = await apiService.createAnalysis(payload);
      
      toast.dismiss(loadingToast);
      toast.success('Анализ готов!');
      
      // ИСПРАВЛЕНО: Используем `result.analysis_id` из ответа API
      navigate(`/analysis/${result.analysis_id}`);

    } catch (error: any) {
      toast.dismiss(loadingToast);
      if (axios.isAxiosError(error)) {
        const detail = (error.response?.data as any)?.detail;
        let message = 'Ошибка анализа';
        if (Array.isArray(detail)) {
          message = detail.map((e) => e.msg).join('; ');
        } else if (typeof detail === 'string') {
          message = detail;
        }
        toast.error(message);
      } else {
        toast.error('Неизвестная ошибка анализа');
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        {/* ... ваш JSX для хедера без изменений ... */}
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Upload Section - немного изменена для UX */}
          <div className={`bg-white rounded-lg shadow-md p-6 transition-opacity ${!includeResume ? 'opacity-50' : ''}`}>
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Upload className="w-5 h-5 text-primary-600" />
              1. Загрузите резюме (если нужно)
            </h2>
            <div {...getRootProps()} className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer ...`}>
              {/* ... ваш JSX для dropzone без изменений ... */}
            </div>
            {uploadedFile && (
              <div className="mt-4 p-4 bg-green-50 rounded-lg">
                <p className="text-sm font-medium text-green-800">✓ {uploadedFile.filename}</p>
              </div>
            )}
          </div>

          {/* Analysis Section - здесь основные изменения */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary-600" />
              2. Настройте и запустите анализ
            </h2>
            <p className="text-gray-600 mb-6">
              Выберите источники данных, которые система будет использовать для построения рекомендаций.
            </p>

            {/* НОВОЕ: Чекбоксы для выбора */}
            <div className="space-y-4 mb-6">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="pgd-checkbox"
                  checked={includePgd}
                  onChange={(e) => setIncludePgd(e.target.checked)}
                  className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <label htmlFor="pgd-checkbox" className="ml-3 flex items-center gap-2 text-sm text-gray-900">
                  <BrainCircuit className="w-5 h-5 text-gray-500" />
                  Психографическая матрица (PGD)
                </label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="resume-checkbox"
                  checked={includeResume}
                  onChange={(e) => setIncludeResume(e.target.checked)}
                  className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <label htmlFor="resume-checkbox" className="ml-3 flex items-center gap-2 text-sm text-gray-900">
                  <FileSignature className="w-5 h-5 text-gray-500" />
                  Данные из резюме
                </label>
              </div>
            </div>

            <button
              onClick={handleStartAnalysis}
              // ИСПРАВЛЕНО: Новая логика для disabled
              disabled={isAnalyzing || (includeResume && !uploadedFile) || (!includePgd && !includeResume)}
              className="w-full bg-primary-600 text-white py-3 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isAnalyzing ? "Анализируем..." : "Запустить анализ"}
            </button>
            
            {/* ... ваш JSX для кнопки "История анализов" и нижних карточек без изменений ... */}
          </div>
        </div>
      </main>
    </div>
  );
};
