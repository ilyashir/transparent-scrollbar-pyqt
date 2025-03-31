#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест производительности скроллбаров в реальном сценарии использования.
Создает окно с большим числом виджетов и тестирует скорость прокрутки.
"""

import sys
import os
import time
import random
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                            QMainWindow, QScrollArea, QPushButton)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QColor, QLinearGradient, QPalette

# Добавляем родительский каталог в путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Импортируем нашу реализацию
from transparent_scroller import apply_overlay_scrollbars

# Количество виджетов для теста
NUM_WIDGETS = 200
# Количество операций прокрутки для теста
NUM_SCROLL_OPS = 100

class FancyWidget(QWidget):
    """Красивый виджет с градиентом и содержимым для теста прокрутки"""
    
    def __init__(self, index):
        super().__init__()
        self.setFixedHeight(80)
        self.setMinimumWidth(300)
        
        # Создаем градиентный фон
        gradient = QLinearGradient(0, 0, 0, 80)
        h = (index * 20) % 360
        gradient.setColorAt(0, QColor.fromHsv(h, 120, 240))
        gradient.setColorAt(1, QColor.fromHsv((h + 40) % 360, 160, 210))
        
        # Устанавливаем фон
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, gradient)
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        
        # Добавляем содержимое виджета
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        title = QLabel(f"Элемент {index + 1}")
        title.setStyleSheet("font-weight: bold; color: white; font-size: 14px;")
        
        description = QLabel(f"Это тестовый элемент №{index + 1} для проверки скорости прокрутки")
        description.setStyleSheet("color: rgba(255, 255, 255, 200);")
        description.setWordWrap(True)
        
        button = QPushButton("Действие")
        button.setFixedWidth(80)
        
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(button, 0, Qt.AlignmentFlag.AlignRight)


class TestWindow(QMainWindow):
    """Тестовое окно с прокруткой"""
    
    def __init__(self, use_custom_scrollbars=False):
        super().__init__()
        self.setWindowTitle("Тест скроллбаров в реальном сценарии")
        self.setGeometry(100, 100, 500, 600)
        
        # Создаем центральный виджет с контейнером
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем контейнер для виджетов
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # Добавляем множество виджетов
        for i in range(NUM_WIDGETS):
            widget = FancyWidget(i)
            container_layout.addWidget(widget)
        
        # Создаем область прокрутки
        if use_custom_scrollbars:
            # Используем наши оптимизированные скроллбары
            scroll_area = apply_overlay_scrollbars(
                container,
                auto_hide=True,
                use_dark_theme=True
            )
        else:
            # Используем стандартные скроллбары Qt
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(container)
        
        # Размещаем область прокрутки в центральном виджете
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
        
        # Сохраняем ссылку на область прокрутки
        self.scroll_area = scroll_area
    
    def test_scrolling_performance(self):
        """Тестирует производительность прокрутки"""
        print("Запуск теста производительности прокрутки...")
        
        # Получаем вертикальный скроллбар
        scrollbar = self.scroll_area.verticalScrollBar()
        
        # Получаем диапазон скроллбара
        min_val = scrollbar.minimum()
        max_val = scrollbar.maximum()
        page_step = scrollbar.pageStep()
        
        # Возможные операции прокрутки
        operations = [
            # Прокрутка на страницу вниз
            lambda: scrollbar.setValue(min(max_val, scrollbar.value() + page_step)),
            # Прокрутка на страницу вверх
            lambda: scrollbar.setValue(max(min_val, scrollbar.value() - page_step)),
            # Прокрутка на небольшое расстояние вниз
            lambda: scrollbar.setValue(min(max_val, scrollbar.value() + page_step // 4)),
            # Прокрутка на небольшое расстояние вверх
            lambda: scrollbar.setValue(max(min_val, scrollbar.value() - page_step // 4)),
            # Прокрутка к случайной позиции
            lambda: scrollbar.setValue(random.randint(min_val, max_val))
        ]
        
        # Прогрев (для более стабильных результатов)
        print("Прогрев...", end="", flush=True)
        for _ in range(20):
            random.choice(operations)()
            QApplication.processEvents()
        print(" готово")
        
        # Засекаем время
        start_time = time.time()
        
        # Выполняем операции прокрутки
        for i in range(NUM_SCROLL_OPS):
            # Выбираем случайную операцию
            op = random.choice(operations)
            op()
            
            # Обрабатываем события для обновления интерфейса
            QApplication.processEvents()
            
            # Небольшая задержка для имитации реального использования
            if i % 5 == 0:
                time.sleep(0.01)
        
        # Вычисляем затраченное время
        elapsed_time = time.time() - start_time
        
        print(f"Тест завершен за {elapsed_time:.4f} секунд")
        return elapsed_time


def run_test():
    """Запускает тест производительности скроллбаров"""
    app = QApplication(sys.argv)
    
    # Тест со стандартными скроллбарами
    print("\nТест со стандартными скроллбарами Qt:")
    window_standard = TestWindow(use_custom_scrollbars=False)
    window_standard.show()
    time_standard = window_standard.test_scrolling_performance()
    window_standard.close()
    
    # Тест с оптимизированными скроллбарами
    print("\nТест с оптимизированными скроллбарами:")
    window_optimized = TestWindow(use_custom_scrollbars=True)
    window_optimized.show()
    time_optimized = window_optimized.test_scrolling_performance()
    window_optimized.close()
    
    # Выводим результаты
    print("\nРезультаты теста в реальном сценарии:")
    print(f"Стандартные скроллбары Qt: {time_standard:.4f} секунд")
    print(f"Оптимизированные скроллбары: {time_optimized:.4f} секунд")
    
    # Вычисляем разницу
    if time_standard > 0:
        improvement = (time_standard - time_optimized) / time_standard * 100
        times_faster = time_standard / time_optimized if time_optimized > 0 else float('inf')
        
        print(f"\nУлучшение производительности: {'+' if improvement > 0 else ''}{improvement:.2f}%")
        print(f"Оптимизированные скроллбары быстрее в {times_faster:.2f} раза")
    
    # Выходим с кодом успеха независимо от результатов производительности
    # Результаты теста только информативные
    return 0


if __name__ == "__main__":
    sys.exit(run_test()) 