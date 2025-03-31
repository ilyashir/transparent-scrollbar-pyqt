import sys
import os
import time
from PyQt6.QtWidgets import QApplication, QScrollBar, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QPixmap

# Добавляем родительскую директорию в путь для доступа к модулю
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Количество итераций в тесте
ITERATIONS = 5000

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест производительности")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Создаем скроллбары для теста
        self.normal_scrollbar = SimplePaintScrollBar()
        self.pixmap_scrollbar = PixmapScrollBar()
        
        layout.addWidget(self.normal_scrollbar)
        layout.addWidget(self.pixmap_scrollbar)
        
        self.show()
    
    def run_test(self):
        """Запускает тест производительности"""
        print("Тест производительности рендеринга скроллбаров")
        print("=" * 50)
        
        # Тест обычного рендеринга
        print(f"Тест без кэширования QPixmap ({ITERATIONS} итераций)...")
        time_normal = self._test_scrollbar(self.normal_scrollbar)
        print(f"Время: {time_normal:.4f} секунд")
        
        # Тест рендеринга с кэшем QPixmap
        print(f"\nТест с кэшированием QPixmap ({ITERATIONS} итераций)...")
        time_pixmap = self._test_scrollbar(self.pixmap_scrollbar)
        print(f"Время: {time_pixmap:.4f} секунд")
        
        # Сравнение результатов
        if time_normal > 0:
            improvement = (time_normal - time_pixmap) / time_normal * 100
            times_faster = time_normal / time_pixmap if time_pixmap > 0 else float('inf')
            
            print("\nРезультаты:")
            print(f"Улучшение производительности: {improvement:.2f}%")
            print(f"Рендеринг с QPixmap быстрее в {times_faster:.2f} раза")
    
    def _test_scrollbar(self, scrollbar):
        """Тестирует производительность рендеринга скроллбара"""
        # Прогрев
        for i in range(10):
            scrollbar.setValue(i)
            scrollbar.update()
            QApplication.processEvents()
        
        # Измеряем время
        start_time = time.time()
        
        for i in range(ITERATIONS):
            scrollbar.setValue(i % 100)
            scrollbar.update()
            QApplication.processEvents()
        
        end_time = time.time()
        return end_time - start_time

class SimplePaintScrollBar(QScrollBar):
    """Базовый скроллбар с простым рендерингом"""
    
    def __init__(self):
        super().__init__(Qt.Orientation.Vertical)
        self.setRange(0, 100)
        self.setPageStep(10)
        self.setFixedSize(20, 400)
        self.bg_color = QColor(200, 200, 200, 50)
        self.handle_color = QColor(100, 100, 100, 150)
        self.border_color = QColor(80, 80, 80, 200)
        self.highlight_color = QColor(220, 220, 220, 100)
    
    def paintEvent(self, event):
        """Простая отрисовка без кэширования"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем фон
        painter.fillRect(self.rect(), self.bg_color)
        
        # Рисуем ползунок
        handle_rect = self._calculate_handle_rect()
        painter.fillRect(handle_rect, self.handle_color)
        
        # Дополнительные элементы для усложнения рендеринга (градиентный эффект)
        painter.setPen(self.border_color)
        painter.drawRoundedRect(handle_rect, 5, 5)
        
        # Добавляем градиентный эффект (имитация)
        for i in range(5):
            small_rect = handle_rect.adjusted(i, i, -i, -i)
            color = QColor(self.highlight_color)
            color.setAlpha(150 - i * 20)
            painter.setPen(color)
            painter.drawRoundedRect(small_rect, 5-i, 5-i)
        
        # Рисуем дополнительные линии для визуального эффекта
        painter.setPen(QColor(250, 250, 250, 40))
        for i in range(0, self.height(), 10):
            painter.drawLine(0, i, self.width(), i)
    
    def _calculate_handle_rect(self):
        """Вычисляет положение и размер ползунка"""
        min_val = self.minimum()
        max_val = self.maximum()
        page_step = self.pageStep()
        val = self.value()
        
        # Размер ползунка относительно видимой части
        handle_ratio = min(1.0, page_step / (max_val - min_val + page_step))
        height = max(30, int(self.height() * handle_ratio))
        
        # Позиция ползунка
        available_space = self.height() - height
        if max_val > min_val:
            pos_ratio = (val - min_val) / (max_val - min_val)
        else:
            pos_ratio = 0
        
        pos = int(available_space * pos_ratio)
        
        return QRect(2, pos, self.width() - 4, height)

class PixmapScrollBar(SimplePaintScrollBar):
    """Скроллбар с кэшированием рендеринга через QPixmap"""
    
    def __init__(self):
        super().__init__()
        self._pixmap_cache = None
        self._last_value = None
    
    def paintEvent(self, event):
        """Отрисовка с использованием кэша QPixmap"""
        # Проверяем, нужно ли обновить кэш
        if self._pixmap_cache is None or self._last_value != self.value():
            self._pixmap_cache = self._render_to_pixmap()
            self._last_value = self.value()
        
        # Рисуем кэшированное изображение
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pixmap_cache)
    
    def _render_to_pixmap(self):
        """Рендерит содержимое в QPixmap"""
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем фон
        painter.fillRect(self.rect(), self.bg_color)
        
        # Рисуем ползунок
        handle_rect = self._calculate_handle_rect()
        painter.fillRect(handle_rect, self.handle_color)
        
        # Дополнительные элементы для усложнения рендеринга
        painter.setPen(self.border_color)
        painter.drawRoundedRect(handle_rect, 5, 5)
        
        # Добавляем градиентный эффект (имитация)
        for i in range(5):
            small_rect = handle_rect.adjusted(i, i, -i, -i)
            color = QColor(self.highlight_color)
            color.setAlpha(150 - i * 20)
            painter.setPen(color)
            painter.drawRoundedRect(small_rect, 5-i, 5-i)
        
        # Рисуем дополнительные линии для визуального эффекта
        painter.setPen(QColor(250, 250, 250, 40))
        for i in range(0, self.height(), 10):
            painter.drawLine(0, i, self.width(), i)
        
        painter.end()
        return pixmap

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.run_test()
    
    # Закрываем окно после выполнения тестов
    window.close()
    
    # Получаем результаты теста для определения кода возврата
    time_normal = window._test_scrollbar(window.normal_scrollbar)
    time_pixmap = window._test_scrollbar(window.pixmap_scrollbar)
    
    # Выходим с кодом 0 (успех), если оптимизированная версия быстрее
    # или с кодом 1 (ошибка), если оптимизация не работает
    sys.exit(0 if time_pixmap < time_normal else 1) 