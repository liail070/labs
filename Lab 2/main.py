"""Консольное приложение для проверки и поиска римских чисел."""

import argparse
import sys

import requests

from roman_numerals import (
    fetch_url,
    find_roman_numbers,
    is_valid_roman,
    read_text_file,
)


def print_search_results(source_name: str, text: str) -> None:
    """Выводит найденные числа и их количество."""
    numbers = find_roman_numbers(text)
    print(f"\nИсточник: {source_name}")
    if not numbers:
        print("Корректные римские числа не найдены.")
        return

    print(f"Найдено чисел: {len(numbers)}")
    for index, number in enumerate(numbers, start=1):
        print(f"{index}. {number}")


def run_interactive() -> None:
    """Запускает меню для пользовательского ввода."""
    while True:
        print("\n=== Работа с римскими числами ===")
        print("1. Проверить одно число")
        print("2. Найти числа в тексте")
        print("3. Найти числа в файле")
        print("4. Найти числа на веб-странице")
        print("0. Выход")

        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                value = input("Введите римское число: ")
                if is_valid_roman(value):
                    print(f"{value.strip()} — корректное римское число.")
                else:
                    print("Некорректная запись. Допустимый диапазон: I–MMMCMXCIX.")
            elif choice == "2":
                text = input("Введите текст: ")
                print_search_results("пользовательский текст", text)
            elif choice == "3":
                path = input("Путь к текстовому файлу: ").strip()
                print_search_results(path, read_text_file(path))
            elif choice == "4":
                url = input("URL веб-страницы: ").strip()
                print_search_results(url, fetch_url(url))
            elif choice == "0":
                print("Работа завершена.")
                return
            else:
                print("Неизвестный пункт меню. Повторите ввод.")
        except (OSError, ValueError, requests.RequestException) as error:
            print(f"Ошибка: {error}")


def main() -> int:
    """Обрабатывает аргументы командной строки или запускает меню."""
    parser = argparse.ArgumentParser(
        description="Проверка и поиск синтаксически корректных римских чисел."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", metavar="NUMBER", help="проверить одно число")
    group.add_argument("--text", metavar="TEXT", help="найти числа в тексте")
    group.add_argument("--file", metavar="PATH", help="искать числа в файле")
    group.add_argument("--url", metavar="URL", help="искать числа на веб-странице")
    args = parser.parse_args()

    try:
        if args.check is not None:
            valid = is_valid_roman(args.check)
            print("Корректное римское число." if valid else "Некорректное римское число.")
        elif args.text is not None:
            print_search_results("переданный текст", args.text)
        elif args.file is not None:
            print_search_results(args.file, read_text_file(args.file))
        elif args.url is not None:
            print_search_results(args.url, fetch_url(args.url))
        else:
            run_interactive()
    except (OSError, ValueError, requests.RequestException) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
