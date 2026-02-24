import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { apiService } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';
import toast from 'react-hot-toast';
import { Upload, FileText, Sparkles, LogOut, BarChart3 } from 'lucide-react';
import axios from 'axios';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<any>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const document = await apiService.uploadDocument(file);
      setUploadedFile(document);
      toast.success('Файл успешно загружен!');
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

  const handleStartAnalysis = async () => {
    if (!uploadedFile) {
      toast.error('Сначала загрузите резюме');
      return;
    }

    if (!user) {
      toast.error('Пользователь не найден');
      return;
    }

    const name = user.full_name || user.email;
    const date_of_birth = user.date_of_birth || ''; // ожидается "DD.MM.YYYY"
    const gender = user.gender || '';               // ожидается "М" или "Ж"

    setIsAnalyzing(true);
    try {
      const payload = {
        name,
        date_of_birth,
        gender,
        client_document_id: uploadedFile.id,
        include_documents: true,
      };
      console.log('createAnalysis payload:', payload);

      const analysis = await apiService.createAnalysis(payload);
      toast.success('Анализ готов!');
      navigate(`/analysis/${analysis.id}`);
    } catch (error: any) {
      if (axios.isAxiosError(error)) {
        const detail = (error.response?.data as any)?.detail;
        console.log('analysis/create error detail:', detail);

        let message = 'Ошибка анализа';
        if (Array.isArray(detail)) {
          message = detail.map((e) => e.msg).join('; ');
        } else if (typeof detail === 'string') {
          message = detail;
        }

        toast.error(message);
      } else {
        toast.error('Ошибка анализа');
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
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">
            Career Intelligence Platform
          </h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">
              Привет, {user?.full_name || user?.email}!
            </span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
            >
              <LogOut className="w-4 h-4" />
              Выйти
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Upload className="w-5 h-5 text-primary-600" />
              Загрузите резюме
            </h2>

            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-300 hover:border-primary-400'
              }`}
            >
              <input {...getInputProps()} />
              <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              {isUploading ? (
                <p className="text-gray-600">Загрузка...</p>
              ) : isDragActive ? (
                <p className="text-gray-600">Отпустите файл здесь</p>
              ) : (
                <div>
                  <p className="text-gray-600 mb-2">
                    Перетащите файл сюда или кликните для выбора
                  </p>
                  <p className="text-sm text-gray-400">
                    Поддерживаются: PDF, DOCX, TXT
                  </p>
                </div>
              )}
            </div>

            {uploadedFile && (
              <div className="mt-4 p-4 bg-green-50 rounded-lg">
                <p className="text-sm font-medium text-green-800">
                  ✓ {uploadedFile.filename}
                </p>
                <p className="text-xs text-green-600 mt-1">
                  Навыки: {uploadedFile.extracted_skills?.hard_skills?.length || 0} hard skills,{' '}
                  {uploadedFile.extracted_skills?.soft_skills?.length || 0} soft skills
                </p>
              </div>
            )}
          </div>

          {/* Analysis Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary-600" />
              AI-анализ карьеры
            </h2>

            <p className="text-gray-600 mb-6">
              Наша система проанализирует вашу психографическую матрицу (PGD),
              навыки из резюме и предоставит персональные рекомендации по карьерному развитию.
            </p>

            <button
              onClick={handleStartAnalysis}
              disabled={!uploadedFile || isAnalyzing}
              className="w-full bg-primary-600 text-white py-3 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isAnalyzing ? (
                <>Анализируем...</>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Запустить анализ
                </>
              )}
            </button>

            <div className="mt-6 pt-6 border-t">
              <button
                onClick={() => navigate('/history')}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                <BarChart3 className="w-5 h-5" />
                История анализов
              </button>
            </div>
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="font-semibold text-lg mb-2">📊 PGD-матрица</h3>
            <p className="text-gray-600 text-sm">
              Психографический анализ личности на основе даты рождения
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="font-semibold text-lg mb-2">🎯 Карьерные треки</h3>
            <p className="text-gray-600 text-sm">
              Персональные рекомендации по профессиональному развитию
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="font-semibold text-lg mb-2">💼 Soft/Hard Skills</h3>
            <p className="text-gray-600 text-sm">
              Оценка баланса навыков и рекомендации по развитию
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};
