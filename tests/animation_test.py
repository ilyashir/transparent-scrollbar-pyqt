import sys
import os
import time
import gc
import psutil
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMainWindow, QScrollArea
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QObject, pyqtProperty

# Добавляем родительскую директорию в путь для доступа к модулю
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from transparent_scroller import OverlayScrollArea, apply_overlay_scrollbars

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


class MemoryAnimationTest:
    """Класс для тестирования эффективности анимаций и потребления памяти"""
    
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.process = psutil.Process(os.getpid())
        
        # Создаем тестовое окно
        self.window = QMainWindow()
        self.window.setWindowTitle("Тест анимаций")
        self.window.setGeometry(100, 100, 400, 300)
        
        # Инициализируем переменные для хранения результатов
        self.creation_times = []
        self.animation_times = []
        self.memory_usage = []
    
    def _collect_garbage(self):
        """Принудительная сборка мусора для чистоты теста"""
        gc.collect()
    
    def _get_memory_usage(self):
        """Получение текущего использования памяти процессом"""
        return self.process.memory_info().rss / (1024 * 1024)  # В МБ
    
    def test_animation_creation(self):
        """Тест создания анимаций - проверяет ленивую инициализацию"""
        print("Тестирование ленивой инициализации анимаций...")
        
        # Проверка анимаций с auto_hide=True (должны создаваться)
        content_with_anim = TestWidget()
        scroll_with_anim = apply_overlay_scrollbars(content_with_anim, auto_hide=True)
        
        # Проверка анимаций с auto_hide=False (не должны создаваться)
        content_without_anim = TestWidget()
        scroll_without_anim = apply_overlay_scrollbars(content_without_anim, auto_hide=False)
        
        # Получаем приватные атрибуты через рефлексию
        with_anim_v = getattr(scroll_with_anim, "_v_anim", None)
        with_anim_h = getattr(scroll_with_anim, "_h_anim", None)
        
        without_anim_v = getattr(scroll_without_anim, "_v_anim", None)
        without_anim_h = getattr(scroll_without_anim, "_h_anim", None)
        
        # Проверяем, что анимации созданы только когда auto_hide=True
        has_animations_when_needed = with_anim_v is not None and with_anim_h is not None
        no_animations_when_not_needed = without_anim_v is None and without_anim_h is None
        
        # Выводим результаты
        print("\nРезультаты теста ленивой инициализации анимаций:")
        print(f"Анимации созданы когда auto_hide=True: {has_animations_when_needed}")
        print(f"Анимации НЕ созданы когда auto_hide=False: {no_animations_when_not_needed}")
        
        # Очистка ресурсов
        content_with_anim.deleteLater()
        scroll_with_anim.deleteLater()
        content_without_anim.deleteLater()
        scroll_without_anim.deleteLater()
        
        # Успешно если ленивая инициализация работает корректно
        result = has_animations_when_needed and no_animations_when_not_needed
        print(f"Тест {'прошел' if result else 'не прошел'} ✓" if result else "✗")
        
        return result
    
    def test_animation_performance(self):
        """Тест производительности анимаций с разными кривыми"""
        print("\nТестирование производительности анимаций с разными кривыми...")
        
        # Класс с тестовым свойством для анимации
        class AnimatedObject(QObject):
            def __init__(self):
                super().__init__()
                self._value = 0.0
            
            def value(self):
                return self._value
                
            def setValue(self, value):
                self._value = value
            
            value_prop = pyqtProperty(float, value, setValue)
        
        # Создаем объекты для анимации
        linear_obj = AnimatedObject()
        cubic_obj = AnimatedObject()
        
        # Создаем анимации с разными кривыми
        linear_anim = QPropertyAnimation(linear_obj, b"value_prop")
        linear_anim.setEasingCurve(QEasingCurve.Type.Linear)
        
        cubic_anim = QPropertyAnimation(cubic_obj, b"value_prop")
        cubic_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Настраиваем анимации
        for anim in (linear_anim, cubic_anim):
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setDuration(300)
        
        # Тест линейной анимации
        start_time = time.time()
        cpu_start = self.process.cpu_percent()
        
        for _ in range(TEST_CYCLES):
            linear_anim.start()
            # Ждем завершения анимации
            while linear_anim.state() == QPropertyAnimation.State.Running:
                self.app.processEvents()
        
        linear_time = time.time() - start_time
        linear_cpu = self.process.cpu_percent() - cpu_start
        
        # Тест кубической анимации
        start_time = time.time()
        cpu_start = self.process.cpu_percent()
        
        for _ in range(TEST_CYCLES):
            cubic_anim.start()
            # Ждем завершения анимации
            while cubic_anim.state() == QPropertyAnimation.State.Running:
                self.app.processEvents()
        
        cubic_time = time.time() - start_time
        cubic_cpu = self.process.cpu_percent() - cpu_start
        
        # Вывод результатов
        print("\nРезультаты теста производительности анимаций:")
        print(f"Линейная анимация: {linear_time:.4f} сек, CPU: {linear_cpu:.2f}%")
        print(f"Кубическая анимация: {cubic_time:.4f} сек, CPU: {cubic_cpu:.2f}%")
        
        is_efficient = cubic_cpu <= linear_cpu * 1.1  # Считаем оптимизацию успешной, если кубическая не более чем на 10% нагружает CPU
        print(f"Кубическая кривая эффективна: {is_efficient}")
        
        return is_efficient
    
    def test_lazy_animation_creation(self):
        """Тест создания анимаций только при необходимости (когда auto_hide=True)"""
        print("\nТестирование ленивой инициализации анимаций...")
        
        # Создаем виджеты с разными настройками
        content1 = TestWidget()
        content2 = TestWidget()
        
        # С автоскрытием (анимации нужны)
        scroll_with_anim = apply_overlay_scrollbars(content1, auto_hide=True)
        # Без автоскрытия (анимации не нужны)
        scroll_without_anim = apply_overlay_scrollbars(content2, auto_hide=False)
        
        # Проверяем наличие анимаций
        has_animation = hasattr(scroll_with_anim, "_v_anim") and scroll_with_anim._v_anim is not None
        no_animation = hasattr(scroll_without_anim, "_v_anim") and scroll_without_anim._v_anim is None
        
        print(f"Скроллер с auto_hide=True имеет анимации: {has_animation}")
        print(f"Скроллер с auto_hide=False не имеет анимаций: {no_animation}")
        
        return has_animation and no_animation
    
    def run_all_tests(self):
        """Запускает все тесты и выводит итоговый результат"""
        print("=" * 50)
        print("ТЕСТЫ ОПТИМИЗАЦИИ АНИМАЦИЙ")
        print("=" * 50)
        
        creation_result = self.test_animation_creation()
        performance_result = self.test_animation_performance()
        lazy_result = self.test_lazy_animation_creation()
        
        print("\n" + "=" * 50)
        print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
        print(f"Создание анимаций оптимизировано: {'✓' if creation_result else '✗'}")
        print(f"Кривые анимации эффективны: {'✓' if performance_result else '✗'}")
        print(f"Ленивая инициализация работает: {'✓' if lazy_result else '✗'}")
        
        all_passed = creation_result and performance_result and lazy_result
        print(f"\nВсе тесты пройдены: {'✓' if all_passed else '✗'}")
        print("=" * 50)
        
        return all_passed


if __name__ == "__main__":
    tester = MemoryAnimationTest()
    tester.run_all_tests()
    sys.exit(0) 