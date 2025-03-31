import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow, QTextEdit
from PyQt6.QtCore import Qt

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем нужные классы из нашего модуля
from transparent_scroller import (
    BaseScrollBar, 
    VerticalScrollBar, 
    HorizontalScrollBar, 
    ScrollBarAnimationManager,
    ScrollBarThemeManager,
    OverlayScrollArea,
    apply_overlay_scrollbars,
    toggle_scrollbar_theme
)


class StructureTest(unittest.TestCase):
    """Тест для проверки структурного разделения кода скроллбаров"""
    
    @classmethod
    def setUpClass(cls):
        # Инициализируем приложение Qt
        cls.app = QApplication.instance() or QApplication(sys.argv)
    
    def setUp(self):
        # Создаем виджет для тестирования
        self.widget = QTextEdit()
        self.widget.setText("Тестовый текст\n" * 100)  # Создаем контент для прокрутки
    
    def test_base_scrollbar(self):
        """Тест базового класса скроллбара"""
        # Создаем базовый скроллбар
        scrollbar = BaseScrollBar(Qt.Orientation.Vertical)
        
        # Проверяем, что он не реализует метод _calculateOrientedRect
        with self.assertRaises(NotImplementedError):
            scrollbar._calculateSliderRect()
    
    def test_vertical_scrollbar(self):
        """Тест вертикального скроллбара"""
        # Создаем вертикальный скроллбар
        scrollbar = VerticalScrollBar()
        
        # Проверяем, что он наследуется от BaseScrollBar
        self.assertIsInstance(scrollbar, BaseScrollBar)
        
        # Проверяем, что он корректно устанавливает ориентацию
        self.assertEqual(scrollbar._orientation, Qt.Orientation.Vertical)
        
        # Проверяем, что он имеет анимационный менеджер
        self.assertIsInstance(scrollbar.animation_manager, ScrollBarAnimationManager)
    
    def test_horizontal_scrollbar(self):
        """Тест горизонтального скроллбара"""
        # Создаем горизонтальный скроллбар
        scrollbar = HorizontalScrollBar()
        
        # Проверяем, что он наследуется от BaseScrollBar
        self.assertIsInstance(scrollbar, BaseScrollBar)
        
        # Проверяем, что он корректно устанавливает ориентацию
        self.assertEqual(scrollbar._orientation, Qt.Orientation.Horizontal)
        
        # Проверяем, что он имеет анимационный менеджер
        self.assertIsInstance(scrollbar.animation_manager, ScrollBarAnimationManager)
    
    def test_animation_manager(self):
        """Тест менеджера анимаций"""
        # Создаем скроллбар и менеджер анимаций
        scrollbar = VerticalScrollBar(auto_hide=True)
        manager = scrollbar.animation_manager
        
        # Проверяем, что анимации инициализированы
        self.assertIsNotNone(manager.show_animation)
        self.assertIsNotNone(manager.hide_animation)
        self.assertIsNotNone(manager.hide_timer)
        
        # Проверяем, что начальная прозрачность установлена правильно
        self.assertEqual(scrollbar._opacity, 0.0)
        
        # Проверяем обработку событий
        manager.handle_widget_event("enter")
        # Проверка, что анимация показа запустилась (сложно проверить напрямую)
        
        manager.handle_widget_event("leave")
        # Проверка, что таймер для скрытия запустился (сложно проверить напрямую)
    
    def test_theme_manager(self):
        """Тест менеджера тем"""
        # Получаем цвета для светлой темы
        light_theme = ScrollBarThemeManager.get_theme_colors(False)
        
        # Получаем цвета для темной темы
        dark_theme = ScrollBarThemeManager.get_theme_colors(True)
        
        # Проверяем, что темы разные
        self.assertNotEqual(light_theme, dark_theme)
        
        # Проверяем, что каждая тема содержит нужные ключи
        for theme in [light_theme, dark_theme]:
            self.assertIn("bg_color", theme)
            self.assertIn("handle_color", theme)
            self.assertIn("hover_color", theme)
            self.assertIn("pressed_color", theme)
    
    def test_overlay_scroll_area(self):
        """Тест области прокрутки с накладываемыми скроллбарами"""
        # Создаем область прокрутки
        scroll_area = OverlayScrollArea(self.widget)
        
        # Проверяем, что скроллбары корректно созданы
        self.assertIsInstance(scroll_area._v_scroll, VerticalScrollBar)
        self.assertIsInstance(scroll_area._h_scroll, HorizontalScrollBar)
        
        # Проверяем, что стандартные скроллбары скрыты
        self.assertEqual(scroll_area.verticalScrollBarPolicy(), Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.assertEqual(scroll_area.horizontalScrollBarPolicy(), Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
    def test_helper_functions(self):
        """Тест вспомогательных функций"""
        # Тестируем функцию apply_overlay_scrollbars
        scroll_area = apply_overlay_scrollbars(self.widget)
        
        # Проверяем, что возвращен объект правильного типа
        self.assertIsInstance(scroll_area, OverlayScrollArea)
        
        # Тестируем функцию toggle_scrollbar_theme
        toggle_scrollbar_theme(scroll_area, True)
        
        # Проверяем, что тема изменилась
        self.assertTrue(scroll_area._use_dark_theme)
        
        # Проверяем, что тема применена к скроллбарам
        self.assertTrue(scroll_area._v_scroll.use_dark_theme)
        self.assertTrue(scroll_area._h_scroll.use_dark_theme)


def run_all_tests():
    """Запускает все тесты структуры"""
    # Создаем набор тестов
    suite = unittest.TestLoader().loadTestsFromTestCase(StructureTest)
    
    # Запускаем тесты
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    # Выводим результат
    print("\nРезультат тестов структуры:")
    print(f"Выполнено: {result.testsRun}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Провалов: {len(result.failures)}")
    
    # Возвращаем True, если все тесты успешны
    return len(result.errors) == 0 and len(result.failures) == 0


if __name__ == "__main__":
    run_all_tests() 