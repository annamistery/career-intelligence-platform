import logging
import json
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

import google.generativeai as genai
from google.api_core.exceptions import DeadlineExceeded

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)


@dataclass
class AIAnalysisResult:
    """Результат AI-анализа с разделёнными полями insights и recommendations."""
    insights: str
    recommendations: str
    full_text: str


class AIAnalysisService:
    """
    Сервис для карьерного анализа с использованием Gemini.
    Поддерживает три режима: PGD, резюме, или совместный анализ.
    """

    def __init__(self):
        """Инициализация AI-сервиса с моделью Gemini."""
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config={
                "temperature": settings.GEMINI_TEMPERATURE,
                "top_p": 0.9,
                "max_output_tokens": settings.GEMINI_MAX_TOKENS,
            },
        )

    async def generate_analysis(
        self,
        name: str,
        date_of_birth: str,
        gender: str,
        pgd_result: Optional[Dict[str, Any]] = None,
        resume_text: Optional[str] = None,
        use_pgd: bool = True,
        use_resume: bool = True,
    ) -> AIAnalysisResult:
        """
        Генерирует карьерный анализ на основе выбранных источников данных.
        """
        if use_pgd and not pgd_result:
            raise ValueError("Анализ по PGD запрошен, но данные pgd_result не предоставлены.")
        if use_resume and not resume_text:
            raise ValueError("Анализ по резюме запрошен, но текст resume_text не предоставлен.")
        if not use_pgd and not use_resume:
            raise ValueError("Необходимо выбрать хотя бы один источник данных (PGD или резюме).")

        user_data = {"full_name": name, "date_of_birth": date_of_birth, "gender": gender}

        extracted_skills: Optional[Dict[str, List[str]]] = None
        if use_resume and resume_text:
            logger.info("Извлечение навыков из резюме...")
            extracted_skills = await self._extract_skills_from_resume(resume_text)
            logger.info(f"Извлечено навыков: {extracted_skills}")

        prompt = self._create_career_analysis_prompt(
            user_data=user_data,
            pgd_data=pgd_result if use_pgd else None,
            document_text=resume_text if use_resume else None,
            extracted_skills=extracted_skills,
        )
        
        full_text = await self._generate_text_from_prompt(prompt)
        
        insights, recommendations = self._split_analysis(full_text)
        
        return AIAnalysisResult(
            insights=insights,
            recommendations=recommendations,
            full_text=full_text,
        )

    async def _extract_skills_from_resume(self, resume_text: str) -> Dict[str, List[str]]:
        """Использует Gemini для извлечения hard и soft skills из текста резюме."""
        prompt = f"""
        Проанализируй следующий текст резюме и извлеки из него hard-skills (технические и предметные навыки) 
        и soft-skills (личные качества, коммуникативные навыки).
        Верни результат в виде JSON-объекта со следующей структурой:
        {{
          "hard_skills": ["навык1", "навык2", ...],
          "soft_skills": ["навык1", "навык2", ...]
        }}
        ТЕКСТ РЕЗЮМЕ:\n{resume_text[:4000]}
        """
        try:
            response_text = await self._generate_text_from_prompt(prompt)
            cleaned_response = response_text.strip().replace("```json", "").replace("```", "")
            skills_data = json.loads(cleaned_response)
            return {
                "hard_skills": skills_data.get("hard_skills", []),
                "soft_skills": skills_data.get("soft_skills", []),
            }
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Не удалось извлечь и распарсить навыки из резюме: {e}")
            return {"hard_skills": [], "soft_skills": []}

    # ### ИЗМЕНЕНО: Метод использует ВАШ промпт для постановки задачи ###
    def _create_career_analysis_prompt(
        self,
        user_data: Dict[str, Any],
        pgd_data: Optional[Dict[str, Any]],
        document_text: Optional[str],
        extracted_skills: Optional[Dict[str, List[str]]],
    ) -> str:
        """Создает комплексный промпт для анализа из доступных данных."""
        
        prompt_parts = [
            "Ты — эксперт по карьерному консультированию и HR-аналитике с 20-летним опытом работы.",
            "Твоя задача — провести глубокий анализ личности и предоставить профессиональные рекомендации по карьерному развитию.",
            f"\nДАННЫЕ ПОЛЬЗОВАТЕЛЯ:\nИмя: {user_data.get('full_name', 'Не указано')}\n"
            f"Дата рождения: {user_data.get('date_of_birth', 'Не указано')}\n"
            f"Пол: {user_data.get('gender', 'Не указано')}\n",
        ]

        if pgd_data:
            prompt_parts.append("ПСИХОГРАФИЧЕСКИЙ ПРОФИЛЬ (PGD-МАТРИЦА):")
            prompt_parts.append(self._format_pgd_data(pgd_data))

        if document_text and extracted_skills:
            prompt_parts.append("ДАННЫЕ ИЗ РЕЗЮМЕ:")
            prompt_parts.append(f"Извлеченные hard skills: {', '.join(extracted_skills.get('hard_skills', [])) or 'Не обнаружены'}")
            prompt_parts.append(f"Извлеченные soft skills: {', '.join(extracted_skills.get('soft_skills', [])) or 'Не обнаружены'}")
            prompt_parts.append(f"Текст резюме:\n{document_text[:4000]}...\n")
        
        # --- НАЧАЛО БЛОКА С ВАШИМ ПРОМПТОМ ---
        # Формулируем основу для анализа
        analysis_basis = " и ".join(filter(None, ["PGD-матрицы" if pgd_data else None, "данных резюме" if document_text else None]))

        # Подставляем основу в ваш шаблон
        task_prompt = f"""ТВОЯ ЗАДАЧА:

1\. \*\*ГЛУБОКИЙ АНАЛИЗ ЛИЧНОСТИ\*\* (2-3 абзаца):
   - Проанализируй психографический профиль на основе {analysis_basis}
   - Определи ключевые черты характера, мотивацию, стиль работы
   - Укажи сильные стороны и зоны роста

2\. \*\*КАРЬЕРНЫЕ ТРЕКИ\*\* (минимум 3 варианта):
   Для каждого трека укажи:
   - Название профессии/направления
   - Почему это подходит (на основе предоставленных данных)
   - Match score (0-100%)
   - Ключевые сильные стороны для этой роли
   - Области для развития
   Формат:
   \### ТРЕК 1: \[Название\]
   \*\*Match Score: X%\*\*
   \*\*Описание:\*\* \[2-3 предложения\]
   \*\*Сильные стороны:\*\* \[список\]
   \*\*Развивать:\*\* \[список\]

3\. \*\*БАЛАНС НАВЫКОВ\*\*:
   - Оцени текущий уровень soft skills (0-100)
   - Оцени текущий уровень hard skills (0-100)
   - Укажи соотношение (например, 65% soft / 35% hard)
   - Дай рекомендации по балансу

4\. \*\*ДЕТАЛИЗАЦИЯ НАВЫКОВ\*\*:
   Классифицируй все обнаруженные навыки по категориям:
   - \*\*Лидерство и управление\*\*
   - \*\*Коммуникация и эмпатия\*\*
   - \*\*Технические навыки\*\*
   - \*\*Аналитические способности\*\*
   - \*\*Креативность и инновации\*\*

5\. ### РЕКОМЕНДАЦИИ ПО РАЗВИТИЮ (конкретные шаги):
   - Ближайшие 3 месяца
   - 6-12 месяцев
   - Долгосрочная стратегия (1-3 года)

ВАЖНО:
\- Пиши на русском языке
\- Говори от имени карьерного кансультанта, не назыввай своего имени
\- Не называй технические детали, цифры арканов или термины расчёта
\- Обращайся к пользователю по имени
\- Будь конкретным и практичным
\- Используй профессиональный, но дружелюбный тон
\- НЕ используй markdown для жирного текста (\*\*), только для заголовков (###)
"""
        prompt_parts.append(task_prompt)
        # --- КОНЕЦ БЛОКА С ВАШИМ ПРОМПТОМ ---

        return "\n".join(prompt_parts)

    def _format_pgd_data(self, pgd_data: Dict[str, Any]) -> str:
        """Форматирует данные PGD для промпта."""
        formatted = "Основная чашка:\n"
        main_cup = pgd_data.get("main_cup", {})
        for key, value in main_cup.items():
            if value is not None: formatted += f"  {key}: {value}\n"
        
        formatted += "\nРодовые данности:\n"
        ancestral = pgd_data.get("ancestral_data", {})
        for key, value in ancestral.items():
            if value is not None: formatted += f"  {key}: {value}\n"

        formatted += "\nПерекрёсток (индивидуальные аспекты):\n"
        crossroads = pgd_data.get("crossroads", {})
        for key, value in crossroads.items():
            if value is not None: formatted += f"  {key}: {value}\n"

        tasks = pgd_data.get("tasks", {})
        if tasks:
            formatted += "\nКармические задачи:\n"
            for key, value in tasks.items():
                if value is not None: formatted += f"  {key}: {value}\n"
        
        return formatted

    async def _generate_text_from_prompt(self, prompt: str) -> str:
        """Отправляет промпт в Gemini API и возвращает текстовый результат с ретраями."""
        for attempt in range(2):
            try:
                logger.info("Отправка запроса в Gemini API... (попытка %s)", attempt + 1)
                response = await self.model.generate_content_async(prompt)
                if response.text:
                    logger.info("Ответ от Gemini успешно получен.")
                    return response.text.strip()
                raise ValueError("Gemini вернул пустой ответ.")
            except DeadlineExceeded as e:
                logger.warning("Gemini DeadlineExceeded на попытке %s: %s", attempt + 1, e)
                if attempt == 1:
                    logger.error("Gemini не ответил после нескольких попыток: %s", e)
                    raise
            except Exception as e:
                logger.error("Ошибка при генерации ответа от Gemini: %s", e)
                raise
        raise RuntimeError("Не удалось сгенерировать ответ после нескольких попыток.")

    def _split_analysis(self, text: str) -> tuple[str, str]:
        """Разбивает полный текст на insights и recommendations."""
        keywords = ["РЕКОМЕНДАЦИИ", "РЕКОМЕНДАЦИЯ", "DEVELOPMENT", "RECOMMENDATIONS"]
        for kw in keywords:
            idx = text.upper().find(kw)
            if idx != -1:
                return text[:idx].strip(), text[idx:].strip()
        split_at = int(len(text) * 0.66)
        return text[:split_at].strip(), text[split_at:].strip()

    def parse_analysis_for_structured_data(self, analysis_text: str) -> Dict[str, Any]:
        """Извлекает структурированные данные из текста анализа."""
        import re
        career_tracks = []
        track_pattern = (
            r"### ТРЕК \d+: (.+?)\n\*\*Match Score: (\d+)%\*\*\n\*\*Описание:\*\* (.+?)\n"
            r"\*\*Сильные стороны:\*\* (.+?)\n\*\*Развивать:\*\* (.+?)(?=\n###|\Z)"
        )
        matches = re.findall(track_pattern, analysis_text, re.DOTALL)
        for match in matches:
            title, score, description, strengths, development = match
            career_tracks.append({
                "title": title.strip(), "match_score": float(score),
                "description": description.strip(),
                "key_strengths": [s.strip() for s in strengths.split(",")],
                "development_areas": [d.strip() for d in development.split(",")],
            })

        soft_score_match = re.search(r"soft skills.*?(\d+)", analysis_text, re.IGNORECASE)
        hard_score_match = re.search(r"hard skills.*?(\d+)", analysis_text, re.IGNORECASE)

        return {
            "career_tracks": career_tracks,
            "soft_skills_score": float(soft_score_match.group(1)) if soft_score_match else 50.0,
            "hard_skills_score": float(hard_score_match.group(1)) if hard_score_match else 50.0,
        }
