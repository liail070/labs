"""Unit-тесты проверки и поиска римских чисел."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from roman_numerals import (
    fetch_url,
    find_roman_numbers,
    is_valid_roman,
    read_text_file,
)


class TestRomanValidation(unittest.TestCase):
    """Проверки корректных и некорректных форм записи."""

    def test_valid_basic_numbers(self):
        for value in ("I", "II", "III", "IV", "V", "IX", "X", "XL", "L", "XC", "C", "CD", "D", "CM", "M"):
            with self.subTest(value=value):
                self.assertTrue(is_valid_roman(value))

    def test_valid_composite_numbers(self):
        for value in ("XIV", "XLII", "MCMXCIV", "MMXXIV", "MMMCMXCIX"):
            with self.subTest(value=value):
                self.assertTrue(is_valid_roman(value))

    def test_valid_lowercase_and_mixed_case(self):
        self.assertTrue(is_valid_roman("xiv"))
        self.assertTrue(is_valid_roman("mCmXcIv"))

    def test_surrounding_whitespace_is_ignored(self):
        self.assertTrue(is_valid_roman("  XIV  "))

    def test_invalid_repetitions_and_subtractions(self):
        for value in ("IIII", "VV", "XXXX", "CCCC", "DD", "MMMM", "IC", "IL", "VX", "XM", "IIV", "XXL"):
            with self.subTest(value=value):
                self.assertFalse(is_valid_roman(value))

    def test_invalid_characters_and_empty_values(self):
        for value in ("", " ", "ABC", "X1", "1", "IV!", "I V", "N", "0"):
            with self.subTest(value=value):
                self.assertFalse(is_valid_roman(value))

    def test_non_string_input(self):
        self.assertFalse(is_valid_roman(None))
        self.assertFalse(is_valid_roman(14))


class TestRomanSearch(unittest.TestCase):
    """Проверки поиска чисел внутри текста."""

    def test_finds_several_numbers(self):
        self.assertEqual(
            find_roman_numbers("Глава IV, том XII и часть MCMXCIV."),
            ["IV", "XII", "MCMXCIV"],
        )

    def test_search_is_case_insensitive(self):
        self.assertEqual(find_roman_numbers("mix и xiv"), ["mix", "xiv"])

    def test_does_not_match_inside_words(self):
        self.assertEqual(find_roman_numbers("MIXED text CIVIL"), [])

    def test_does_not_take_prefix_of_invalid_long_sequence(self):
        self.assertEqual(find_roman_numbers("IIII VVV IC"), [])

    def test_punctuation_boundaries(self):
        self.assertEqual(find_roman_numbers("(XIV), [IX]; MMXX."), ["XIV", "IX", "MMXX"])

    def test_empty_text(self):
        self.assertEqual(find_roman_numbers(""), [])

    def test_non_string_search_input(self):
        with self.assertRaises(TypeError):
            find_roman_numbers(None)


class TestFileAndUrlSources(unittest.TestCase):
    """Проверки чтения локального файла и загрузки URL."""

    def test_reads_utf8_file(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "sample.txt"
            file_path.write_text("Глава IX и глава X.", encoding="utf-8")
            self.assertEqual(read_text_file(str(file_path)), "Глава IX и глава X.")

    def test_missing_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            read_text_file("file_that_does_not_exist_12345.txt")

    def test_fetch_url_returns_response_text(self):
        response = Mock()
        response.text = "<p>Chapter IV</p>"
        response.encoding = "utf-8"
        with patch("roman_numerals.requests.get", return_value=response) as get:
            result = fetch_url("https://example.com/page")
        self.assertEqual(result, "<p>Chapter IV</p>")
        get.assert_called_once()

    def test_fetch_url_rejects_invalid_url(self):
        with self.assertRaises(ValueError):
            fetch_url("ftp://example.com")

    def test_fetch_url_propagates_http_errors(self):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("404")
        with patch("roman_numerals.requests.get", return_value=response):
            with self.assertRaises(requests.HTTPError):
                fetch_url("https://example.com/missing")


if __name__ == "__main__":
    unittest.main()
