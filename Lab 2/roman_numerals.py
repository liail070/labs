"""Проверка и поиск корректных римских чисел."""

import re
from pathlib import Path
from typing import List
from urllib.parse import urlparse

import requests


# Каноническая запись целых чисел от I (1) до MMMCMXCIX (3999).
# Тысячи: M{0,3}; сотни, десятки и единицы задаются отдельными группами,
# чтобы исключить некорректные формы вроде IIII, IC и VX.
ROMAN_NUMBER_PATTERN = (
    r"M{0,3}"
    r"(?:CM|CD|D?C{0,3})"
    r"(?:XC|XL|L?X{0,3})"
    r"(?:IX|IV|V?I{0,3})"
)
ROMAN_NUMBER_RE = re.compile(
    rf"(?<![A-Za-z])(?=[MDCLXVI])({ROMAN_NUMBER_PATTERN})(?![A-Za-z])",
    re.IGNORECASE,
)
FULL_ROMAN_NUMBER_RE = re.compile(
    rf"^(?:{ROMAN_NUMBER_PATTERN})$", re.IGNORECASE
)


def is_valid_roman(value: str) -> bool:
    """Возвращает True, если строка целиком содержит число от I до MMMCMXCIX."""
    if not isinstance(value, str):
        return False
    normalized = value.strip()
    return bool(normalized and FULL_ROMAN_NUMBER_RE.fullmatch(normalized))


def find_roman_numbers(text: str) -> List[str]:
    """Находит корректные римские числа в тексте, не захватывая части слов."""
    if not isinstance(text, str):
        raise TypeError("Текст для поиска должен быть строкой.")
    return [match.group(1) for match in ROMAN_NUMBER_RE.finditer(text)]


def read_text_file(file_path: str) -> str:
    """Читает текстовый файл в UTF-8."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Файл не найден: {path}")
    return path.read_text(encoding="utf-8")


def fetch_url(url: str, timeout: int = 10) -> str:
    """Загружает текст веб-страницы по HTTP/HTTPS URL."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Укажите корректный URL, начинающийся с http:// или https://.")

    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "RomanNumeralLab/1.0"},
    )
    response.raise_for_status()
    # requests автоматически определяет кодировку из заголовков/содержимого.
    response.encoding = response.encoding or response.apparent_encoding
    return response.text
