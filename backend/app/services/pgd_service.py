"""
PGD calculation service - refactored from original pgd_bot.py
All calculations use modulo 22.

ИСПРАВЛЕНИЯ:
1. Конструктор PGDCalculator больше не требует обязательных аргументов —
   они передаются в метод calculate() (или get_full_analysis()).
   Причина: analysis.py вызывал PGDCalculator() без аргументов → TypeError.

2. Добавлен публичный метод calculate(date_of_birth, gender) — именно его
   вызывает analysis.py. Метод возвращает PGDCalculationResponse-совместимый dict.

3. get_full_analysis() сохранён как алиас с поддержкой старого интерфейса
   (name + date + sex через конструктор).
"""
from typing import Dict, Optional, Any
from collections import Counter


class PGDCalculator:
    """Service for calculating PGD (Psychographic Diagnosis) matrix."""

    def __init__(self, name: str = "", date: str = "", sex: str = ""):
        """
        Initialize PGD calculator.

        BUG FIX: все аргументы сделаны необязательными (default=""),
        чтобы можно было создавать PGDCalculator() без параметров,
        а данные передавать в calculate() / get_full_analysis().

        Args:
            name: Person's name (optional, used for legacy interface)
            date: Birth date in DD.MM.YYYY format (optional)
            sex:  Gender М or Ж (optional)
        """
        self.name = name
        self.date = date
        self.sex = sex.upper() if sex else ""

    # ------------------------------------------------------------------
    # BUG FIX: новый публичный метод, который вызывает analysis.py
    # ------------------------------------------------------------------
    def calculate(
        self,
        date_of_birth: str,
        gender: str,
    ) -> "PGDCalculationResponse":  # type: ignore[name-defined]
        """
        Рассчитать полную PGD-матрицу и вернуть Pydantic-совместимый объект.

        Args:
            date_of_birth: дата рождения в формате DD.MM.YYYY
            gender: пол М или Ж

        Returns:
            Словарь, совместимый с PGDCalculationResponse
        """
        # Временно устанавливаем атрибуты, чтобы переиспользовать
        # приватную логику calculate_points / calculate_tasks / calculate_business_periods
        self.date = date_of_birth
        self.sex = gender.upper()

        points = self.calculate_points()
        tasks = self.calculate_tasks()
        business = self.calculate_business_periods()

        # Возвращаем dict, Pydantic сам разберёт его в PGDCalculationResponse
        return {
            **points,
            "tasks": tasks,
            **(business or {}),
        }

    # ------------------------------------------------------------------
    # Исходные методы (без изменений)
    # ------------------------------------------------------------------
    def calculate_points(self) -> Dict[str, Dict[str, Optional[int]]]:
        """
        Calculate all PGD matrix points.

        Returns:
            Dictionary with main cup, ancestral data, and crossroads
        """
        try:
            X1, X2, X3 = map(int, self.date.split('.'))
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid date format: {self.date}. Expected DD.MM.YYYY")

        # Main cup calculations
        point_A = X1 % 22
        point_B = X2
        sum_year = sum([int(d) for d in str(X3)])
        point_V = sum_year % 22
        point_G = (point_A + point_B + point_V) % 22
        point_D = (point_A + point_B) % 22
        point_L = (22 - point_D) % 22
        point_E = (point_B + point_V) % 22
        point_K = (22 - point_E) % 22
        point_J = (point_D + point_E) % 22
        point_Z = (abs(point_D - point_E) + point_J) % 22
        point_I = (point_J + point_Z) % 22
        point_Y = (point_A + point_V + point_Z) % 22

        # Gender-specific points
        point_M = point_N = point_O = point_P = None

        if self.sex == 'Ж':
            point_M = (point_G + point_I + point_L) % 22
            point_N = (point_M + point_Y) % 22
        elif self.sex == 'М':
            point_O = (point_G + point_I + point_K) % 22
            point_P = (point_O + point_Y) % 22

        # Ancestral data
        RSD = point_J

        if self.sex == 'Ж':
            ROPP = (point_L + point_E) % 22
        elif self.sex == 'М':
            ROPP = (point_D + point_K) % 22
        else:
            ROPP = None

        RCO = (RSD + ROPP) % 22 if ROPP is not None else None
        RUS = point_I

        # Crossroads (individual aspects)
        if self.sex == 'Ж':
            ISD = abs(RSD - point_N) if point_N is not None else None
            IOPP = abs(ROPP - point_N) if ROPP is not None and point_N is not None else None
            IUS = abs(RUS - point_N) if point_N is not None else None
        elif self.sex == 'М':
            ISD = abs(RSD - point_P) if point_P is not None else None
            IOPP = abs(ROPP - point_P) if ROPP is not None and point_P is not None else None
            IUS = abs(RUS - point_P) if point_P is not None else None
        else:
            ISD = IOPP = IUS = None

        ICO = (ISD + IOPP) % 22 if ISD is not None and IOPP is not None else None

        return {
            "main_cup": {
                "A": point_A, "B": point_B, "V": point_V, "G": point_G,
                "D": point_D, "L": point_L, "E": point_E, "K": point_K,
                "J": point_J, "Z": point_Z, "I": point_I, "Y": point_Y,
                "M": point_M, "N": point_N, "O": point_O, "P": point_P
            },
            "ancestral_data": {
                "RSD": RSD,
                "ROPP": ROPP,
                "RCO": RCO,
                "RUS": RUS
            },
            "crossroads": {
                "ISD": ISD,
                "IOPP": IOPP,
                "ICO": ICO,
                "IUS": IUS
            }
        }

    def calculate_tasks(self) -> Dict[str, Optional[int]]:
        """
        Calculate karmic tasks based on repeating values.

        Returns:
            Dictionary with KR (karma of genus), LKO (personal karma), BN (divine tax)
        """
        dict_points = self.calculate_points()

        # Karma of Genus (KR): ≥3 repeats in main cup
        lst_1 = [v for v in dict_points["main_cup"].values() if v is not None]
        counter_1 = Counter(lst_1)
        result_1 = [elem for elem in set(lst_1) if counter_1[elem] >= 3]
        KR = sum(result_1) % 22 if result_1 else None

        # Personal Karma of Relationships (LKO): ≥3 repeats in main cup + ancestral
        lst_2 = [v for v in dict_points["main_cup"].values() if v is not None]
        lst_2 += [v for v in dict_points["ancestral_data"].values() if v is not None]
        counter_2 = Counter(lst_2)
        result_2 = [elem for elem in set(lst_2) if counter_2[elem] >= 3]
        LKO = sum(result_2) % 22 if result_2 else None

        # Divine Tax (BN): ≥3 repeats in main cup + crossroads
        lst_3 = [v for v in dict_points["main_cup"].values() if v is not None]
        lst_3 += [v for v in dict_points["crossroads"].values() if v is not None]
        counter_3 = Counter(lst_3)
        result_3 = [elem for elem in set(lst_3) if counter_3[elem] >= 3]
        BN = sum(result_3) % 22 if result_3 else None

        return {
            "karma_of_genus": KR,
            "personal_karma_relationships": LKO,
            "divine_tax": BN
        }

    def calculate_business_periods(self) -> Optional[Dict[str, Dict[str, Optional[int]]]]:
        """
        Calculate business periods based on repeating values.

        Returns:
            Dictionary with 4 business periods or None
        """
        dict_points = self.calculate_points()

        lst_1 = [v for v in dict_points["main_cup"].values() if v is not None]
        counter = Counter(lst_1)
        result_1 = [elem for elem in set(lst_1) if counter[elem] >= 2]

        if not result_1:
            return None

        # Period 1: values 1-10
        values_1 = [x for x in result_1 if 1 <= x <= 10]
        period_1 = sum(values_1) % 22 if values_1 else None

        # Period 2: values 11-20
        values_2 = [x for x in result_1 if 11 <= x <= 20]
        period_2 = sum(values_2) % 22 if values_2 else None

        # Period 3: values 0 or 21
        values_3 = [x for x in result_1 if x in (0, 21)]
        period_3 = sum(values_3) % 22 if values_3 else None

        # Period 4: sum of all defined periods
        if any(p is not None for p in (period_1, period_2, period_3)):
            period_4 = sum(
                p for p in (period_1, period_2, period_3) if p is not None
            ) % 22
        else:
            period_4 = None

        return {
            "business_periods": {
                "period_1": period_1,
                "period_2": period_2,
                "period_3": period_3,
                "period_4": period_4
            }
        }

    def get_full_analysis(self) -> Dict[str, Any]:
        """
        Get complete PGD analysis (legacy interface — используется через конструктор).

        Returns:
            Dictionary with all calculations
        """
        return {
            **self.calculate_points(),
            "tasks": self.calculate_tasks(),
            "business_periods": self.calculate_business_periods()
        }
