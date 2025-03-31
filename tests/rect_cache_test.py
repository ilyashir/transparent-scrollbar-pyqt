#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест для проверки эффективности кэширования расчетов ползунка скроллбара.
"""

import sys
import time
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QScrollBar
from PyQt6.QtCore import Qt, QRect

# Добавляем родительский каталог в путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Импортируем нашу оптимизированную версию
from transparent_scroller import TransparentScroller

# Константы для тестирования
TEST_CYCLES = 10000  # Количество циклов для теста

class RawScrollBar(QScrollBar):
    """Базовая версия скроллера без кэширования расчетов ползунка"""
    
    def __init__(self, orientation):
        super().__init__(orientation)
        self.setStyleSheet("background-color: transparent;")
        
    def _calculateSliderRect(self):
        """Вычисляет прямоугольник ползунка скроллбара без кэширования"""
        # Получаем основные параметры скроллбара
        minimum = self.minimum()
        maximum = self.maximum()
        page_step = self.pageStep()
        value = self.value()
        
        # Если нет диапазона для прокрутки, занимаем всю доступную область
        if maximum <= minimum:
            return self.rect().adjusted(2, 2, -2, -2)
        
        # Вычисляем размер ползунка в процентах от общего размера скроллбара
        handle_size_ratio = min(1.0, page_step / (maximum - minimum + page_step))
        
        # Вычисляем положение ползунка в процентах
        position_ratio = (value - minimum) / (maximum - minimum)
        
        # Размеры скроллбара
        width = self.width()
        height = self.height()
        
        # Отступы от краев
        margin = 2
        
        if self.orientation() == Qt.Orientation.Vertical:
            # Для вертикального скроллбара
            handle_height = max(20, int(height * handle_size_ratio))
            available_height = height - handle_height
            handle_pos = int(available_height * position_ratio)
            
            return QRect(
                margin, 
                handle_pos, 
                width - 2 * margin, 
                handle_height
            )
        else:
            # Для горизонтального скроллбара
            handle_width = max(20, int(width * handle_size_ratio))
            available_width = width - handle_width
            handle_pos = int(available_width * position_ratio)
            
            return QRect(
                handle_pos, 
                margin, 
                handle_width, 
                height - 2 * margin
            )

class RectCacheTest:
    """Класс для тестирования кэширования расчетов ползунка"""
    
    def __init__(self):
        """Инициализация тестов"""
        self.app = QApplication(sys.argv)
        
        # Создаем тестовые скроллбары
        self.cached_scroll = TransparentScroller(Qt.Orientation.Vertical)
        self.raw_scroll = RawScrollBar(Qt.Orientation.Vertical)
        
        # Настраиваем диапазоны для тестов
        self.cached_scroll.setRange(0, 1000)
        self.cached_scroll.setPageStep(100)
        self.raw_scroll.setRange(0, 1000)
        self.raw_scroll.setPageStep(100)
        
        # Настраиваем размеры скроллбаров
        self.cached_scroll.resize(20, 400)
        self.raw_scroll.resize(20, 400)
    
    def test_calculation_performance(self):
        """Тест производительности вычисления ползунка с кэшированием и без"""
        print("Тестирование производительности вычисления ползунка...")
        print(f"Выполняем {TEST_CYCLES} циклов...")
        
        # Сбрасываем статистику кэша
        self.cached_scroll._cache_hits = 0
        self.cached_scroll._cache_misses = 0
        
        # Тест без кэширования
        start_time = time.time()
        
        for i in range(TEST_CYCLES):
            # Реалистичная имитация прокрутки: 
            # обычно страница прокручивается небольшими шагами
            # и есть множество повторных вызовов для одного значения
            # (например, при отрисовке)
            value = (i // 5) % 1000  # Меняем значение каждые 5 итераций
            self.raw_scroll.setValue(value)
            # Вычисляем прямоугольник ползунка
            rect = self.raw_scroll._calculateSliderRect()
            
        raw_time = time.time() - start_time
        
        # Тест с кэшированием
        start_time = time.time()
        
        for i in range(TEST_CYCLES):
            # Используем ту же последовательность значений
            value = (i // 5) % 1000
            self.cached_scroll.setValue(value)
            # Вычисляем прямоугольник ползунка
            rect = self.cached_scroll._calculateSliderRect()
            
        cached_time = time.time() - start_time
        
        # Выводим результаты
        print("\nРезультаты теста производительности вычисления ползунка:")
        print(f"Без кэширования: {raw_time:.4f} сек")
        print(f"С кэшированием: {cached_time:.4f} сек")
        print(f"Ускорение: {raw_time / cached_time:.2f}x")
        
        # Получаем статистику использования кэша
        cache_stats = self.cached_scroll.getCacheStats()
        print("\nСтатистика использования кэша:")
        print(f"Всего вызовов: {cache_stats['total']}")
        print(f"Попаданий в кэш: {cache_stats['hits']} ({cache_stats['hit_rate']:.2f}%)")
        print(f"Промахов кэша: {cache_stats['misses']}")
        
        return raw_time > cached_time
    
    def test_cache_hit_scenarios(self):
        """Тест различных сценариев для проверки эффективности кэширования"""
        print("\nТестирование сценариев использования кэша...")
        
        # Сценарий 1: Повторные запросы с одинаковым значением
        print("Сценарий 1: Повторные запросы с одинаковым значением")
        self.cached_scroll.setValue(500)
        
        # Сбрасываем статистику кэша
        self.cached_scroll._cache_hits = 0
        self.cached_scroll._cache_misses = 0
        
        # Многократно запрашиваем ползунок без изменения значения
        for _ in range(100):
            rect = self.cached_scroll._calculateSliderRect()
        
        stats = self.cached_scroll.getCacheStats()
        print(f"Процент попаданий в кэш: {stats['hit_rate']:.2f}%")
        scenario1_success = stats['hit_rate'] > 95  # Ожидаем высокий процент попаданий
        
        # Сценарий 2: Чередующиеся значения
        print("\nСценарий 2: Чередующиеся значения")
        
        # Сбрасываем статистику кэша
        self.cached_scroll._cache_hits = 0
        self.cached_scroll._cache_misses = 0
        
        # Чередуем два значения
        for i in range(100):
            # При смене значения кэш должен инвалидироваться
            self.cached_scroll.setValue(300 if i % 2 == 0 else 700)
            # В реальном сценарии, одно и то же значение запрашивается несколько раз
            for _ in range(5):  # Имитируем несколько запросов при одном значении
                rect = self.cached_scroll._calculateSliderRect()
        
        stats = self.cached_scroll.getCacheStats()
        print(f"Процент попаданий в кэш: {stats['hit_rate']:.2f}%")
        scenario2_success = stats['hit_rate'] > 40  # Ожидаем умеренный процент попаданий
        
        # Сценарий 3: Изменение параметров, не влияющих на кэш
        print("\nСценарий 3: Изменение параметров, не влияющих на кэш")
        
        # Сбрасываем статистику кэша
        self.cached_scroll._cache_hits = 0
        self.cached_scroll._cache_misses = 0
        
        # Устанавливаем значение и запрашиваем ползунок
        self.cached_scroll.setValue(500)
        rect = self.cached_scroll._calculateSliderRect()
        
        # Меняем параметр, который не должен инвалидировать кэш
        self.cached_scroll._opacity = 0.8
        rect = self.cached_scroll._calculateSliderRect()
        
        stats = self.cached_scroll.getCacheStats()
        print(f"Процент попаданий в кэш: {stats['hit_rate']:.2f}%")
        scenario3_success = stats['hit_rate'] > 0  # Ожидаем хотя бы одно попадание в кэш
        
        # Общий результат тестов
        overall_success = scenario1_success and scenario2_success and scenario3_success
        print(f"\nОбщий результат тестов сценариев: {'Успех ✓' if overall_success else 'Неудача ✗'}")
        
        return overall_success
    
    def run_all_tests(self):
        """Запускает все тесты и выводит общий результат"""
        print("=" * 50)
        print("ТЕСТ КЭШИРОВАНИЯ РАСЧЕТОВ ПОЛЗУНКА СКРОЛЛБАРА")
        print("=" * 50)
        
        print("Запуск теста производительности...")
        performance_result = self.test_calculation_performance()
        print("Тест производительности завершен.")
        
        print("Запуск теста сценариев использования кэша...")
        scenarios_result = self.test_cache_hit_scenarios()
        print("Тест сценариев использования кэша завершен.")
        
        print("\n" + "=" * 50)
        print("ОБЩИЙ РЕЗУЛЬТАТ ТЕСТОВ:")
        print("=" * 50)
        
        print(f"Тест производительности: {'Успех ✓' if performance_result else 'Неудача ✗'}")
        print(f"Тест сценариев использования кэша: {'Успех ✓' if scenarios_result else 'Неудача ✗'}")
        print(f"Общий результат: {'Успех ✓' if performance_result and scenarios_result else 'Неудача ✗'}")
        
        # Завершаем работу приложения и возвращаемся из функции main
        return

if __name__ == "__main__":
    tester = RectCacheTest()
    tester.run_all_tests() 