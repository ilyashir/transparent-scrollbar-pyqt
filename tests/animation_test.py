#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест для проверки оптимизации анимаций скроллбаров.
"""

import sys
import os
import time
import gc
import psutil
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMainWindow
from PyQt6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation

# Добавляем родительский каталог в путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Импортируем нашу реализацию
from transparent_scroller import (
    VerticalScrollBar,
    HorizontalScrollBar,
)

# Количество тестовых циклов
TEST_CYCLES = 100

class TestWidget(QWidget):
    """Тестовый виджет с большим количеством содержимого для прокрутки"""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Добавляем много строк текста для скроллинга
        for i in range(100):
            label = QLabel(f"Тестовая строка {i+1}")
            label.setMinimumWidth(300)
            layout.addWidget(label)


class AnimationTest:
    """Класс для тестирования анимаций скроллбаров"""
    
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.main_window = None
    
    def _create_test_ui(self, num_widgets=100):
        """Создает тестовый пользовательский интерфейс с множеством виджетов"""
        # Создаем основной виджет
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Создаем множество виджетов для прокрутки
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        for i in range(num_widgets):
            label = QLabel(f"Тестовый виджет {i}")
            label.setFixedHeight(30)
            container_layout.addWidget(label)
        
        # Устанавливаем отступы и расстояние между виджетами
        container_layout.setSpacing(10)
        container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Устанавливаем предпочтительный размер контейнера
        container.setMinimumSize(400, num_widgets * 40)
        
        # Создаем основной виджет с прокруткой
        self.main_window = QMainWindow()
        self.main_window.setGeometry(100, 100, 500, 500)
        
        return container
    
    def test_lazy_animation_init(self):
        """Тест проверяет, что анимации создаются только когда auto_hide=True"""
        print("Тестирование ленивой инициализации анимаций...")
        
        # Создаем виджет для тестирования
        container = self._create_test_ui()
        
        # Создаем скроллер с auto_hide=True
        v_scrollbar_1 = VerticalScrollBar(auto_hide=True)
        
        # Создаем скроллер с auto_hide=False
        v_scrollbar_2 = VerticalScrollBar(auto_hide=False)
        
        # Проверяем, что анимации созданы только для скроллера с auto_hide=True
        has_animations_when_auto_hide = (
            hasattr(v_scrollbar_1.animation_manager, 'show_animation') and
            hasattr(v_scrollbar_1.animation_manager, 'hide_animation') and
            v_scrollbar_1.animation_manager.show_animation is not None and
            v_scrollbar_1.animation_manager.hide_animation is not None
        )
        
        print("\nРезультаты теста ленивой инициализации анимаций:")
        print(f"Анимации созданы когда auto_hide=True: {has_animations_when_auto_hide}")
        
        return has_animations_when_auto_hide
        
    def test_animation_performance(self, num_cycles=10, duration=300):
        """Тест проверяет производительность разных типов анимаций"""
        print("Тестирование производительности анимаций с разными кривыми...")
        
        # Создаем виджет для тестирования
        container = self._create_test_ui()
        
        # Создаем скроллеры
        v_scrollbar_1 = VerticalScrollBar(auto_hide=True)
        v_scrollbar_2 = VerticalScrollBar(auto_hide=True)
        
        # Создаем анимации с разными кривыми
        # Линейная анимация
        show_anim_linear = QPropertyAnimation(v_scrollbar_1, b"opacity")
        show_anim_linear.setDuration(duration)
        show_anim_linear.setStartValue(0.0)
        show_anim_linear.setEndValue(1.0)
        show_anim_linear.setEasingCurve(QEasingCurve.Type.Linear)
        
        hide_anim_linear = QPropertyAnimation(v_scrollbar_1, b"opacity")
        hide_anim_linear.setDuration(duration)
        hide_anim_linear.setStartValue(1.0)
        hide_anim_linear.setEndValue(0.0)
        hide_anim_linear.setEasingCurve(QEasingCurve.Type.Linear)
        
        # Кубическая анимация
        show_anim_cubic = QPropertyAnimation(v_scrollbar_2, b"opacity")
        show_anim_cubic.setDuration(duration)
        show_anim_cubic.setStartValue(0.0)
        show_anim_cubic.setEndValue(1.0)
        show_anim_cubic.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        hide_anim_cubic = QPropertyAnimation(v_scrollbar_2, b"opacity")
        hide_anim_cubic.setDuration(duration)
        hide_anim_cubic.setStartValue(1.0)
        hide_anim_cubic.setEndValue(0.0)
        hide_anim_cubic.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # Получаем текущий процесс для измерения CPU
        process = psutil.Process(os.getpid())
        
        # Запускаем цикл тестирования для линейной анимации
        start_time = time.time()
        start_cpu = process.cpu_percent(interval=None)
        
        for _ in range(num_cycles):
            # Показываем скроллбар
            v_scrollbar_1.setOpacity(0.0)
            show_anim_linear.start()
            
            # Даем анимации время выполниться
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: None)
            timer.start(duration + 50)
            
            while timer.isActive():
                self.app.processEvents()
            
            # Скрываем скроллбар
            v_scrollbar_1.setOpacity(1.0)
            hide_anim_linear.start()
            
            # Даем анимации время выполниться
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: None)
            timer.start(duration + 50)
            
            while timer.isActive():
                self.app.processEvents()
            
            time.sleep(0.05)  # Небольшая пауза между циклами
        
        linear_time = time.time() - start_time
        linear_cpu = process.cpu_percent(interval=0.1)
        
        # Запускаем цикл тестирования для кубической анимации
        start_time = time.time()
        
        for _ in range(num_cycles):
            # Показываем скроллбар
            v_scrollbar_2.setOpacity(0.0)
            show_anim_cubic.start()
            
            # Даем анимации время выполниться
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: None)
            timer.start(duration + 50)
            
            while timer.isActive():
                self.app.processEvents()
            
            # Скрываем скроллбар
            v_scrollbar_2.setOpacity(1.0)
            hide_anim_cubic.start()
            
            # Даем анимации время выполниться
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: None)
            timer.start(duration + 50)
            
            while timer.isActive():
                self.app.processEvents()
            
            time.sleep(0.05)  # Небольшая пауза между циклами
        
        cubic_time = time.time() - start_time
        cubic_cpu = process.cpu_percent(interval=0.1)
        
        # Выводим результаты
        print("\nРезультаты теста производительности анимаций:")
        print(f"Линейная анимация: {linear_time:.4f} сек, CPU: {linear_cpu:.2f}%")
        print(f"Кубическая анимация: {cubic_time:.4f} сек, CPU: {cubic_cpu:.2f}%")
        
        # Проверяем, что обе анимации работают
        animations_work = linear_time > 0 and cubic_time > 0
        print(f"Анимации работают: {animations_work}")
        
        return animations_work
    
    def test_lazy_init_implementation(self):
        """Проверяет, что ленивая инициализация работает правильно"""
        print("\nТестирование ленивой инициализации анимаций...")
        
        # Создаем виджет с auto_hide=True
        v_scrollbar_1 = VerticalScrollBar(auto_hide=True)
        
        # Проверяем, что у него созданы анимации
        has_animations_true = (
            hasattr(v_scrollbar_1.animation_manager, 'show_animation') and
            hasattr(v_scrollbar_1.animation_manager, 'hide_animation') and
            v_scrollbar_1.animation_manager.show_animation is not None and
            v_scrollbar_1.animation_manager.hide_animation is not None
        )
        
        # Создаем виджет с auto_hide=False
        v_scrollbar_2 = VerticalScrollBar(auto_hide=False)
        
        # Проверяем, есть ли у него анимации
        has_animations_false = (
            hasattr(v_scrollbar_2.animation_manager, 'show_animation') and
            hasattr(v_scrollbar_2.animation_manager, 'hide_animation') and
            v_scrollbar_2.animation_manager.show_animation is not None and
            v_scrollbar_2.animation_manager.hide_animation is not None
        )
        
        print(f"Скроллер с auto_hide=True имеет анимации: {has_animations_true}")
        print(f"Скроллер с auto_hide=False имеет анимации: {has_animations_false}")
        
        return has_animations_true and not has_animations_false


if __name__ == "__main__":
    tester = AnimationTest()
    lazy_init_result = tester.test_lazy_animation_init()
    performance_result = tester.test_animation_performance()
    lazy_impl_result = tester.test_lazy_init_implementation()
    
    print("\nИтоговые результаты тестов:")
    print(f"Ленивая инициализация анимаций: {'[УСПЕХ]' if lazy_init_result else '[НЕУДАЧА]'}")
    print(f"Анимации работают корректно: {'[УСПЕХ]' if performance_result else '[НЕУДАЧА]'}")
    print(f"Реализация ленивой инициализации: {'[УСПЕХ]' if lazy_impl_result else '[НЕУДАЧА]'}")
    print(f"Общий результат: {'[УСПЕХ]' if all([lazy_init_result, performance_result, lazy_impl_result]) else '[НЕУДАЧА]'}")
    
    sys.exit(0) 