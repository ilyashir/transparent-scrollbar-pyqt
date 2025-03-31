#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для запуска всех тестов скроллбара.
Запускает последовательно все тесты и выводит общие результаты.
"""

import os
import sys
import time
import subprocess
from colorama import init, Fore, Style

# Инициализация colorama для цветного вывода в консоль Windows
init()

# Пути к тестам относительно этого скрипта
TESTS = [
    "structure_test.py",     # Тест структуры модуля
    "rect_cache_test.py",    # Тест кэширования прямоугольников
    "animation_test.py",     # Тест анимаций
    "simple_test.py",        # Простые функциональные тесты
    "performance_test.py",   # Тесты производительности
    "real_world_test.py"     # Тест в реальном сценарии использования
]

def print_header(text):
    """Выводит заголовок с оформлением"""
    print("\n" + "=" * 80)
    print(f"{Fore.CYAN}{Style.BRIGHT}>>> {text}{Style.RESET_ALL}")
    print("=" * 80)

def print_success(text):
    """Выводит сообщение об успехе"""
    print(f"{Fore.GREEN}{Style.BRIGHT}{text}{Style.RESET_ALL}")

def print_failure(text):
    """Выводит сообщение о неудаче"""
    print(f"{Fore.RED}{Style.BRIGHT}{text}{Style.RESET_ALL}")

def print_info(text):
    """Выводит информационное сообщение"""
    print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")

def run_test(test_path):
    """Запускает отдельный тест и возвращает результат его выполнения"""
    start_time = time.time()
    
    try:
        # Запускаем тест как подпроцесс
        result = subprocess.run(
            [sys.executable, test_path],
            capture_output=True,
            text=True,
            check=False  # Не вызывать исключение при ненулевом коде возврата
        )
        
        success = result.returncode == 0
        execution_time = time.time() - start_time
        
        return {
            "success": success,
            "output": result.stdout,
            "error": result.stderr,
            "time": execution_time,
            "return_code": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "time": time.time() - start_time,
            "return_code": -1
        }

def main():
    """Основная функция запуска всех тестов"""
    # Получаем текущую директорию скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print_header("ЗАПУСК ВСЕХ ТЕСТОВ СКРОЛЛБАРА")
    print(f"Дата и время: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Каталог тестов: {script_dir}")
    print(f"Всего тестов: {len(TESTS)}")
    
    # Статистика выполнения
    results = []
    total_time = 0
    passed = 0
    failed = 0
    
    # Запускаем каждый тест
    for i, test_file in enumerate(TESTS, 1):
        test_path = os.path.join(script_dir, test_file)
        
        if not os.path.exists(test_path):
            print_info(f"\nТест {i}/{len(TESTS)}: {test_file} - файл не найден, пропускаем")
            results.append({
                "name": test_file,
                "success": False,
                "error": "Файл не найден",
                "time": 0
            })
            failed += 1
            continue
            
        print_info(f"\nТест {i}/{len(TESTS)}: {test_file} - запуск...")
        
        # Запускаем тест
        result = run_test(test_path)
        total_time += result["time"]
        results.append({"name": test_file, **result})
        
        # Выводим результат
        if result["success"]:
            print_success(f"УСПЕХ ({result['time']:.2f} сек)")
            passed += 1
        else:
            print_failure(f"НЕУДАЧА ({result['time']:.2f} сек)")
            print(f"Код возврата: {result['return_code']}")
            if result["error"]:
                print(f"Ошибка:\n{result['error']}")
            failed += 1
    
    # Выводим общую статистику
    print_header("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print(f"Всего тестов: {len(TESTS)}")
    print(f"Успешно: {passed}")
    print(f"Неудачно: {failed}")
    print(f"Общее время выполнения: {total_time:.2f} сек")
    
    # Выводим детальную статистику по каждому тесту
    print("\nДетальные результаты:")
    for result in results:
        status = "УСПЕХ" if result["success"] else "НЕУДАЧА"
        color_func = print_success if result["success"] else print_failure
        color_func(f"{result['name']}: {status} ({result['time']:.2f} сек)")
    
    # Возвращаем код ошибки, если хотя бы один тест не прошел
    return 1 if failed > 0 else 0

if __name__ == "__main__":
    sys.exit(main()) 