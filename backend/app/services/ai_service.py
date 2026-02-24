"""
AI analysis service using Google Gemini API.
"""
import logging
from typing import Dict, List, Any, Optional

import google.generativeai as genai
from google.api_core.exceptions import DeadlineExceeded  # тип ошибки таймаута

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)


class AIAnalysisService:
    """Service for AI-powered career analysis using Gemini."""

    def __init__(self):
        """Initialize AI service with Gemini model."""
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config={
                "temperature": settings.GEMINI_TEMPERATURE,
                "top_p": 0.9,
                "max_output_tokens": settings.GEMINI_MAX_TOKENS,
            },
        )

    def _create_career_analysis_prompt(
        self,
        user_data: Dict[str, Any],
        pgd_data: Dict[str, Any],
        document_text: Optional[str] = None,
        extracted_skills: Optional[Dict[str, List[str]]] = None,
    ) -> str:
        """
        Create comprehensive prompt for career analysis.
        """
        # Жёстко ограничим размер текста резюме, чтобы не рвать модель и таймаут
        if document_text:
            document_text = document_text[:4000]

        prompt = f"""Ты — эксперт по карьерному консультированию и HR-аналитике с 20-летним опытом работы.
Твоя задача — провести глубокий анализ личности и предоставить профессиональные рекомендации по карьерному развитию.

ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:
Имя: {user_data.get('full_name', 'Не указано')}
Дата рождения: {user_data.get('date_of_birth', 'Не указано')}
Пол: {user_data.get('gender', 'Не указано')}

ПСИХОГРАФИЧЕСКИЙ ПРОФИЛЬ (PGD-МАТРИЦА):
{self._format_pgd_data(pgd_data)}

"""

        if document_text and extracted_skills:
            prompt += f"""ДАННЫЕ ИЗ РЕЗЮМЕ:

Извлеченные hard skills: {', '.join(extracted_skills.get('hard_skills', [])) or 'Не обнаружены'}

Извлеченные soft skills: {', '.join(extracted_skills.get('soft_skills', [])) or 'Не обнаружены'}

Текст резюме :
{document_text}...

"""

        prompt += """ТВОЯ ЗАДАЧА:

1. **ГЛУБОКИЙ АНАЛИЗ ЛИЧНОСТИ** (2-3 абзаца):
   - Проанализируй психографический профиль на основе PGD-матрицы
   - Определи ключевые черты характера, мотивацию, стиль работы
   - Укажи сильные стороны и зоны роста

2. **КАРЬЕРНЫЕ ТРЕКИ** (минимум 3 варианта):
   Для каждого трека укажи:
   - Название профессии/направления
   - Почему это подходит (на основе PGD + резюме)
   - Match score (0-100%)
   - Ключевые сильные стороны для этой роли
   - Области для развития
   
   Формат:
   ### ТРЕК 1: [Название]
   **Match Score: X%**
   **Описание:** [2-3 предложения]
   **Сильные стороны:** [список]
   **Развивать:** [список]

3. **БАЛАНС НАВЫКОВ**:
   - Оцени текущий уровень soft skills (0-100)
   - Оцени текущий уровень hard skills (0-100)
   - Укажи соотношение (например, 65% soft / 35% hard)
   - Дай рекомендации по балансу

4. **ДЕТАЛИЗАЦИЯ НАВЫКОВ**:
   Классифицируй все обнаруженные навыки по категориям:
   - **Лидерство и управление**
   - **Коммуникация и эмпатия**
   - **Технические навыки**
   - **Аналитические способности**
   - **Креативность и инновации**
   
   Для каждой категории укажи уровень (1-5) и комментарий.

5. **РЕКОМЕНДАЦИИ ПО РАЗВИТИЮ** (конкретные шаги):
   - Ближайшие 3 месяца
   - 6-12 месяцев
   - Долгосрочная стратегия (1-3 года)

ВАЖНО:
- Пиши на русском языке
- Не указывай своего имени, предствься карьерным консультантом
- Не назвай технические детали, цифры арканов, номера точек (Точка A, B, V, G и т.д.) или термины расчёта
- Обращайся к пользователю по имени (найди его в начале файла)
- Будь конкретным и практичным
- Основывай выводы на данных (PGD + резюме)
- Используй профессиональный, но дружелюбный тон
- НЕ используй markdown для жирного текста (**), только для заголовков (###)
"""

        return prompt

    def _format_pgd_data(self, pgd_data: Dict[str, Any]) -> str:
        """Format PGD data for prompt."""
        formatted = "Основная чашка:\n"
        main_cup = pgd_data.get("main_cup", {})
        for key, value in main_cup.items():
            if value is not None:
                formatted += f"  {key}: {value}\n"

        formatted += "\nРодовые данности:\n"
        ancestral = pgd_data.get("ancestral_data", {})
        for key, value in ancestral.items():
            if value is not None:
                formatted += f"  {key}: {value}\n"

        formatted += "\nПерекрёсток (индивидуальные аспекты):\n"
        crossroads = pgd_data.get("crossroads", {})
        for key, value in crossroads.items():
            if value is not None:
                formatted += f"  {key}: {value}\n"

        tasks = pgd_data.get("tasks", {})
        if tasks:
            formatted += "\nКармические задачи:\n"
            for key, value in tasks.items():
                if value is not None:
                    formatted += f"  {key}: {value}\n"

        return formatted

    async def generate_career_analysis(
        self,
        user_data: Dict[str, Any],
        pgd_data: Dict[str, Any],
        document_text: Optional[str] = None,
        extracted_skills: Optional[Dict[str, List[str]]] = None,
    ) -> str:
        """
        Generate comprehensive career analysis.
        """
        prompt = self._create_career_analysis_prompt(
            user_data, pgd_data, document_text, extracted_skills
        )

        # Простой retry на случай временного таймаута Gemini
        for attempt in range(2):
            try:
                logger.info("Sending request to Gemini API... (attempt %s)", attempt + 1)
                response = self.model.generate_content(prompt)

                if response.text:
                    logger.info("Successfully received analysis from Gemini")
                    return response.text.strip()
                else:
                    raise ValueError("Gemini returned empty response")

            except DeadlineExceeded as e:
                logger.warning("Gemini DeadlineExceeded on attempt %s: %s", attempt + 1, e)
                if attempt == 1:
                    logger.error("Gemini failed after retries: %s", e)
                    raise
            except Exception as e:
                logger.error("Error generating analysis: %s", e)
                raise

        # Теоретически сюда не дойдём
        raise RuntimeError("Failed to generate analysis")

    def parse_analysis_for_structured_data(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parse analysis text to extract structured data for database.
        """
        import re

        career_tracks = []
        track_pattern = (
            r"### ТРЕК \d+: (.+?)\n\*\*Match Score: (\d+)%\*\*\n\*\*Описание:\*\* (.+?)\n"
            r"\*\*Сильные стороны:\*\* (.+?)\n\*\*Развивать:\*\* (.+?)(?=\n###|\Z)"
        )
        matches = re.findall(track_pattern, analysis_text, re.DOTALL)

        for match in matches:
            title, score, description, strengths, development = match
            career_tracks.append(
                {
                    "title": title.strip(),
                    "match_score": float(score),
                    "description": description.strip(),
                    "key_strengths": [s.strip() for s in strengths.split(",")],
                    "development_areas": [d.strip() for d in development.split(",")],
                }
            )

        soft_score = 50.0
        hard_score = 50.0

        soft_match = re.search(r"soft skills.*?(\d+)", analysis_text, re.IGNORECASE)
        if soft_match:
            soft_score = float(soft_match.group(1))

        hard_match = re.search(r"hard skills.*?(\d+)", analysis_text, re.IGNORECASE)
        if hard_match:
            hard_score = float(hard_match.group(1))

        return {
            "career_tracks": career_tracks,
            "soft_skills_score": soft_score,
            "hard_skills_score": hard_score,
        }
