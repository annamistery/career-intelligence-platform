import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
// Предполагаем, что ваш apiService экспортирует эти функции
import { apiService } from '@/services/api'; 
import toast from 'react-hot-toast';
import { ArrowLeft } from 'lucide-react';

// Эта страница - аналог AnalysisForm из моих предыдущих ответов.
export const AnalysisFormPage: React.FC = () => {
    const navigate = useNavigate();

    // --- State для полей формы ---
    const [name, setName] = useState('');
    const [dateOfBirth, setDateOfBirth] = useState('');
    const [gender, setGender] = useState('М');

    // --- State для НОВЫХ опций анализа ---
    const [includePgd, setIncludePgd] = useState(true);
    const [includeResume, setIncludeResume] = useState(false);
    
    // State для списка резюме пользователя
    const [userDocuments, setUserDocuments] = useState<{ id: number; filename: string }[]>([]); 
    const [selectedDocumentId, setSelectedDocumentId] = useState('');
    
    // State для UI (загрузка, ошибки)
    const [isLoading, setIsLoading] = useState(false);

    // --- Загрузка списка документов при монтировании ---
    useEffect(() => {
        const loadDocuments = async () => {
            try {
                // Предполагается, что у вас есть метод для получения документов
                const documents = await apiService.getUserDocuments(); 
                setUserDocuments(documents);
            } catch (error) {
                toast.error("Не удалось загрузить список ваших резюме.");
            }
        };
        
        loadDocuments();
    }, []);

    // --- ОБНОВЛЕННАЯ функция отправки формы ---
    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        
        if (includeResume && !selectedDocumentId) {
            toast.error('Пожалуйста, выберите резюме для анализа.');
            return;
        }
        if (!includePgd && !includeResume) {
            toast.error('Выберите хотя бы один источник для анализа.');
            return;
        }

        setIsLoading(true);

        // Формируем тело запроса согласно новой Pydantic-модели в FastAPI
        const analysisData = {
            name,
            date_of_birth: dateOfBirth,
            gender,
            include_pgd: includePgd,
            include_resume: includeResume,
            client_document_id: includeResume ? parseInt(selectedDocumentId, 10) : null,
        };

        try {
            const loadingToast = toast.loading('Создаем анализ... Это может занять до минуты.');
            
            // Вызываем новый метод API
            const result = await apiService.createAnalysis(analysisData);
            
            toast.dismiss(loadingToast);
            toast.success('Анализ успешно создан!');
            
            // Перенаправляем на страницу результатов
            navigate(`/analysis/${result.analysis_id}`);

        } catch (error: any) {
            toast.dismiss(); // Убираем toast загрузки
            toast.error(error.message || 'Произошла ошибка при создании анализа.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow-sm">
                <div className="max-w-4xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        Назад к дашборду
                    </button>
                </div>
            </header>
            
            <main className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
                <div className="bg-white rounded-lg shadow-lg p-8">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <h1 className="text-3xl font-bold text-gray-900">Новый карьерный анализ</h1>
                        
                        {/* --- Основные поля --- */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Имя клиента</label>
                                <input type="text" value={name} onChange={(e) => setName(e.target.value)} required 
                                       className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-primary-500 focus:border-primary-500" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Дата рождения</label>
                                <input type="text" value={dateOfBirth} placeholder="ДД.ММ.ГГГГ" onChange={(e) => setDateOfBirth(e.target.value)} required
                                       className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-primary-500 focus:border-primary-500" />
                            </div>
                        </div>

                        <hr />
                        
                        {/* --- Новые опции --- */}
                        <div>
                            <h2 className="text-xl font-semibold mb-4">Источники данных</h2>
                            <div className="space-y-4">
                                <div className="flex items-center">
                                    <input type="checkbox" id="pgd-checkbox" checked={includePgd} onChange={(e) => setIncludePgd(e.target.checked)}
                                           className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500" />
                                    <label htmlFor="pgd-checkbox" className="ml-3 block text-sm text-gray-900">Учесть психографическую диагностику</label>
                                </div>
                                <div className="flex items-center">
                                    <input type="checkbox" id="resume-checkbox" checked={includeResume} onChange={(e) => setIncludeResume(e.target.checked)}
                                           className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500" />
                                    <label htmlFor="resume-checkbox" className="ml-3 block text-sm text-gray-900">Учесть данные из резюме</g>
                                </div>

                                {includeResume && (
                                    <div className="pl-7 pt-2">
                                        <label className="block text-sm font-medium text-gray-700">Выберите резюме</label>
                                        <select value={selectedDocumentId} onChange={(e) => setSelectedDocumentId(e.target.value)} required
                                                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:ring-primary-500 focus:border-primary-500">
                                            <option value="">-- Выберите документ --</option>
                                            {userDocuments.map(doc => (
                                                <option key={doc.id} value={doc.id}>{doc.filename}</option>
                                            ))}
                                        </select>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="pt-4">
                            <button type="submit" disabled={isLoading}
                                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:bg-gray-400">
                                {isLoading ? 'Создание...' : 'Начать анализ'}
                            </button>
                        </div>
                    </form>
                </div>
            </main>
        </div>
    );
};
