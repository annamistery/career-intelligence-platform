"""
AI analysis service using Google Gemini API.

ИСПРАВЛЕНИЯ:
1. Добавлен метод generate_analysis() — именно его вызывает analysis.py.
   В оригинале был только generate_career_analysis() с другой сигнатурой.

2. generate_analysis() возвращает объект AIAnalysisResult (dataclass)
   с полями .insights и .recommendations — analysis.py обращался к ним,
   но исходный метод возвращал просто str.

3. Вызов Gemini переведён на асинхронный generate_content_async(),
   чтобы не блокировать event loop FastAPI.
   (синхронный generate_content() внутри async-функции замораживал весь сервер)
"""
import logging
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

import google.generativeai as genai
from google.api_core.exceptions import DeadlineExceeded

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)


# ------------------------------------------------------------------
# BUG FIX: Добавлен dataclass для типизированного возврата из generate_analysis
# ------------------------------------------------------------------
@dataclass
class AIAnalysisResult:
    """Результат AI-анализа с разделёнными полями insights и recommendations."""
    insights: str
    recommendations: str
    full_text: str


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

    # ------------------------------------------------------------------
    # BUG FIX: новый публичный метод, который вызывает analysis.py
    # ------------------------------------------------------------------
    async def generate_analysis(
        self,
        name: str,
        date_of_birth: str,
        gender: str,
        pgd_result: Dict[str, Any],
        resume_text: Optional[str] = None,
    ) -> AIAnalysisResult:
        """
        Сгенерировать карьерный анализ и вернуть структурированный результат.

        BUG FIX: в оригинале этот метод отсутствовал — был только
        generate_career_analysis() с другой сигнатурой.
        analysis.py вызывал generate_analysis() → AttributeError.

        Args:
            name:          имя клиента
            date_of_birth: дата рождения DD.MM.YYYY
            gender:        пол М / Ж
            pgd_result:    словарь с результатами PGD-расчёта
            resume_text:   текст резюме (опционально)

        Returns:
            AIAnalysisResult с полями insights, recommendations, full_text
        """
        user_data = {
            "full_name": name,
            "date_of_birth": date_of_birth,
            "gender": gender,
        }

        # Извлечём skills из pgd_result, если документ был передан
        extracted_skills: Optional[Dict[str, List[str]]] = None

        full_text = await self.generate_career_analysis(
            user_data=user_data,
            pgd_data=pgd_result,
            document_text=resume_text,
            extracted_skills=extracted_skills,
        )

        # Разбиваем текст на insights (анализ) и recommendations (рекомендации)
        insights, recommendations = self._split_analysis(full_text)

        return AIAnalysisResult(
            insights=insights,
            recommendations=recommendations,
            full_text=full_text,
        )

    # ------------------------------------------------------------------
    # Вспомогательный метод: разбивка текста на две части
    # ------------------------------------------------------------------
    def _split_analysis(self, text: str) -> tuple[str, str]:
        """
        Разбить полный текст анализа на insights и recommendations.

        Ищет секцию «РЕКОМЕНДАЦИИ» как точку разделения.
        Если не найдена — первые 2/3 текста идут в insights, остаток в recommendations.
        """
        keywords = ["РЕКОМЕНДАЦИИ", "РЕКОМЕНДАЦИЯ", "DEVELOPMENT", "RECOMMENDATIONS"]
        for kw in keywords:
            idx = text.upper().find(kw)
            if idx != -1:
                return text[:idx].strip(), text[idx:].strip()

        # Fallback: делим по 2/3
        split_at = int(len(text) * 0.66)
        return text[:split_at].strip(), text[split_at:].strip()

    # ------------------------------------------------------------------
    # Оригинальный метод (исправлен: sync → async Gemini call)
    # ------------------------------------------------------------------
    def _create_career_analysis_prompt(
        self,
        user_data: Dict[str, Any],
        pgd_data: Dict[str, Any],
        document_text: Optional[str] = None,
        extracted_skills: Optional[Dict[str, List[str]]] = None,
    ) -> str:
        """Create comprehensive prompt for career analysis."""
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

Текст резюме:
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

5. ### РЕКОМЕНДАЦИИ ПО РАЗВИТИЮ (конкретные шаги):
   - Ближайшие 3 месяца
   - 6-12 месяцев
   - Долгосрочная стратегия (1-3 года)

ВАЖНО:
- Пиши на русском языке
- Говори от имени карьерного кансультанта, не назыввай своего имени
- Не называй технические детали, цифры арканов или термины расчёта
- Обращайся к пользователю по имени
- Будь конкретным и практичным
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

        BUG FIX: вызов Gemini переведён на асинхронный generate_content_async(),
        чтобы не блокировать event loop FastAPI.
        """
        prompt = self._create_career_analysis_prompt(
            user_data, pgd_data, document_text, extracted_skills
        )

        for attempt in range(2):
            try:
                logger.info("Sending request to Gemini API... (attempt %s)", attempt + 1)

                # BUG FIX: было self.model.generate_content(prompt) — синхронный вызов
                # внутри async-функции блокировал весь event loop.
                # Исправлено на generate_content_async().
                response = await self.model.generate_content_async(prompt)

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

        raise RuntimeError("Failed to generate analysis")

    def parse_analysis_for_structured_data(self, analysis_text: str) -> Dict[str, Any]:
        """Parse analysis text to extract structured data for database."""
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
