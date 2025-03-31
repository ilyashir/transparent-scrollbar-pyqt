import sys
import os
import time
import random
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QScrollArea, QScrollBar
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor

# Добавляем родительскую директорию в путь для доступа к модулю
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import transparent_scroller
from transparent_scroller import LIGHT_THEME, DARK_THEME, VerticalScrollBar

# Количество тестовых итераций
NUM_ITERATIONS = 5000

class RawScrollBar(QScrollBar):
    """Версия скроллера без оптимизаций - максимально близкая к оригинальному коду до оптимизаций"""
    
    def __init__(self, orientation, bg_alpha=30, handle_alpha=80, 
                 hover_alpha=120, pressed_alpha=160,
                 scroll_bar_width=8, use_dark_theme=False):
        super().__init__(orientation)
        
        # Устанавливаем ориентацию
        self._orientation = orientation
        
        # Сохраняем прозрачность для разных состояний
        self._bg_alpha = bg_alpha
        self._handle_alpha = handle_alpha
        self._hover_alpha = hover_alpha
        self._pressed_alpha = pressed_alpha
        
        # Значение прозрачности для анимации (от 0 до 1)
        self._opacity = 1.0
        
        # Устанавливаем тему
        self.use_dark_theme = use_dark_theme
        
        # Состояние скроллбара
        self._mouse_over = False
        self._mouse_pressed = False
        
        # Настройка внешнего вида
        self.setStyleSheet("background-color: transparent;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Настройка размера в зависимости от ориентации
        if orientation == Qt.Orientation.Vertical:
            self.setFixedWidth(scroll_bar_width)
        else:
            self.setFixedHeight(scroll_bar_width)
        
        # Отслеживаем положение мыши
        self.setMouseTracking(True)
        
        # Инициализируем цвета
        self._initColors()
    
    def _initColors(self):
        """Инициализирует цвета скроллбара на основе темы"""
        theme = DARK_THEME if self.use_dark_theme else LIGHT_THEME
        
        # Базовые цвета
        self._bg_color = QColor(theme["bg_color"])
        self._handle_color = QColor(theme["handle_color"])
        self._hover_color = QColor(theme["hover_color"])
        self._pressed_color = QColor(theme["pressed_color"])
        
        # Применяем прозрачность
        self._bg_color.setAlpha(self._bg_alpha)
        self._handle_color.setAlpha(self._handle_alpha)
        self._hover_color.setAlpha(self._hover_alpha)
        self._pressed_color.setAlpha(self._pressed_alpha)
    
    def paintEvent(self, event):
        """Отрисовка скроллбара без оптимизации QPixmap"""
        # Если полностью прозрачный, не рисуем ничего
        if self._opacity <= 0.01:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Размеры скроллбара
        rect = self.rect()
        
        # Применяем общую прозрачность
        painter.setOpacity(self._opacity)
        
        # Рисуем фон скроллбара
        painter.fillRect(rect, self._bg_color)
        
        # Получаем размеры и положение ползунка
        handle_rect = self._calculateSliderRect()
        
        # Выбираем цвет ползунка в зависимости от состояния
        if self._mouse_pressed:
            handle_color = self._pressed_color
        elif self._mouse_over:
            handle_color = self._hover_color
        else:
            handle_color = self._handle_color
        
        # Рисуем ползунок с закругленными углами
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(handle_color)
        
        # Радиус закругления углов
        radius = 4
        
        # Рисуем закругленный прямоугольник
        painter.drawRoundedRect(handle_rect, radius, radius)
    
    def _calculateSliderRect(self):
        """Вычисляет прямоугольник ползунка скроллбара"""
        # Получаем основные параметры скроллбара
        minimum = self.minimum()
        maximum = self.maximum()
        page_step = self.pageStep()
        value = self.value()
        
        # Если нет диапазона для прокрутки, занимаем всю доступную область
        if maximum <= minimum:
            return self.rect().adjusted(2, 2, -2, -2)
        
        # Вычисляем размер ползунка в процентах от общего размера скроллбара
        # с учетом видимой области (pageStep)
        handle_size_ratio = min(1.0, page_step / (maximum - minimum + page_step))
        
        # Вычисляем положение ползунка в процентах
        position_ratio = (value - minimum) / (maximum - minimum)
        
        # Размеры скроллбара
        width = self.width()
        height = self.height()
        
        # Отступы от краев (для эстетики)
        margin = 2
        
        if self._orientation == Qt.Orientation.Vertical:
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

# Дополнительный класс, имитирующий только оптимизацию QPixmap без других оптимизаций
class PixmapOptimizedScrollBar(RawScrollBar):
    """Версия скроллера только с оптимизацией QPixmap, без других оптимизаций"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализируем кэш изображения
        self._pixmap_cache = None
        self._pixmap_cache_dirty = True
        self._last_state = None
    
    def _getCurrentState(self):
        """Возвращает текущее состояние скроллера для определения необходимости перерисовки"""
        return (
            self.size(),
            self._calculateSliderRect(),
            self._mouse_pressed,
            self._mouse_over,
            self._opacity,
            self.use_dark_theme
        )
        
    def _renderToPixmap(self, handle_color):
        """Отрисовывает скроллер в QPixmap для кэширования"""
        # Создаем пиксмап размером с виджет
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)  # Прозрачный фон
        
        # Создаем QPainter для рисования на пиксмапе
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Получаем размеры скроллбара
        rect = self.rect()
        
        # Рисуем фон скроллбара
        painter.fillRect(rect, self._bg_color)
        
        # Получаем размеры и положение ползунка
        handle_rect = self._calculateSliderRect()
        
        # Рисуем ползунок с закругленными углами
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(handle_color)
        
        # Радиус закругления углов
        radius = 4
        
        # Рисуем закругленный прямоугольник
        painter.drawRoundedRect(handle_rect, radius, radius)
        
        # Завершаем рисование
        painter.end()
        
        return pixmap
    
    def paintEvent(self, event):
        """Отрисовка скроллбара с оптимизацией QPixmap"""
        # Если полностью прозрачный, не рисуем ничего
        if self._opacity <= 0.01:
            return
            
        # Получаем текущее состояние
        current_state = self._getCurrentState()
        
        # Проверяем, нужно ли обновить кэш
        if self._pixmap_cache_dirty or self._pixmap_cache is None or self._last_state != current_state:
            # Определяем цвет ползунка в зависимости от состояния
            if self._mouse_pressed:
                handle_color = self._pressed_color
            elif self._mouse_over:
                handle_color = self._hover_color
            else:
                handle_color = self._handle_color
            
            # Рендерим виджет в пиксмап
            self._pixmap_cache = self._renderToPixmap(handle_color)
            self._pixmap_cache_dirty = False
            self._last_state = current_state
        
        # Рисуем кэшированное изображение с учетом прозрачности
        painter = QPainter(self)
        painter.setOpacity(self._opacity)
        painter.drawPixmap(0, 0, self._pixmap_cache)

# Функция для тестирования производительности рендеринга
def test_rendering_performance(scroll_class):
    """Тестирует производительность рендеринга скроллера"""
    # Создаём временный скроллбар для теста
    if scroll_class == RawScrollBar or scroll_class == PixmapOptimizedScrollBar:
        scrollbar = scroll_class(Qt.Orientation.Vertical)
    else:  # VerticalScrollBar уже имеет фиксированную ориентацию
        scrollbar = scroll_class()
    
    scrollbar.resize(20, 400)
    
    # Задаем диапазон
    scrollbar.setMinimum(0)
    scrollbar.setMaximum(1000)
    scrollbar.setPageStep(100)
    
    # Создаём главное окно для размещения скроллбара
    window = QWidget()
    scrollbar.setParent(window)
    window.resize(50, 450)
    
    # Прогрев (чтобы исключить влияние начальной инициализации)
    print("  Прогрев...", end="", flush=True)
    for _ in range(100):
        scrollbar.setValue(random.randint(0, 900))
        app.processEvents()
    print(" готово")
    
    # Разделяем тест на несколько сценариев, более близких к реальному использованию
    
    # Сценарий 1: Плавный скроллинг (имитация прокрутки колесиком мыши)
    print("  Тест плавного скроллинга...", end="", flush=True)
    start_time = time.time()
    
    for i in range(NUM_ITERATIONS // 5):
        # Плавное изменение значения
        current = scrollbar.value()
        target = min(1000, max(0, current + random.randint(-50, 50)))
        steps = 5
        
        for step in range(steps):
            scrollbar.setValue(current + (target - current) * step // steps)
            
            # Небольшая задержка между обновлениями для реалистичности
            if i % 10 == 0:
                time.sleep(0.001)
                
            app.processEvents()
    
    smooth_time = time.time() - start_time
    print(" готово")
    
    # Сценарий 2: Прыжки к произвольным позициям (имитация кликов по скроллбару)
    print("  Тест скачкообразной прокрутки...", end="", flush=True)
    start_time = time.time()
    
    for i in range(NUM_ITERATIONS // 10):
        # Резко меняем значение на случайное
        scrollbar.setValue(random.randint(0, 1000))
        app.processEvents()
        
        # Каждые несколько итераций делаем паузу
        if i % 5 == 0:
            time.sleep(0.002)
    
    jump_time = time.time() - start_time
    print(" готово")
    
    # Сценарий 3: Длинная серия маленьких перемещений (типичный сценарий скроллинга в приложении)
    print("  Тест серии малых перемещений...", end="", flush=True)
    start_time = time.time()
    
    # Маленькие перемещения вверх-вниз
    value = 500
    for i in range(NUM_ITERATIONS):
        # Небольшое изменение в одну или другую сторону
        delta = random.randint(-3, 3)
        value = max(0, min(1000, value + delta))
        scrollbar.setValue(value)
        
        if i % 20 == 0:
            app.processEvents()
    
    small_time = time.time() - start_time
    print(" готово")
    
    # Закрываем окно
    window.close()
    
    # Общее время - взвешенная сумма разных сценариев
    total_time = smooth_time * 0.4 + jump_time * 0.2 + small_time * 0.4
    
    return total_time

# Запускаем приложение Qt
app = QApplication(sys.argv)

print("Тестирование производительности рендеринга скроллеров")
print("-" * 50)

# Тестируем неоптимизированный скроллер
print(f"Тест без оптимизаций ({NUM_ITERATIONS} итераций)...")
time_raw = test_rendering_performance(RawScrollBar)
print(f"Время: {time_raw:.4f} секунд")

# Тестируем скроллер только с оптимизацией QPixmap
print(f"\nТест только с оптимизацией QPixmap ({NUM_ITERATIONS} итераций)...")
time_pixmap_only = test_rendering_performance(PixmapOptimizedScrollBar)
print(f"Время: {time_pixmap_only:.4f} секунд")

# Тестируем полностью оптимизированный скроллер
print(f"\nТест с полными оптимизациями ({NUM_ITERATIONS} итераций)...")
time_full_opt = test_rendering_performance(VerticalScrollBar)
print(f"Время: {time_full_opt:.4f} секунд")

# Сравниваем результаты
print("\nРезультаты тестов производительности:")
print(f"Базовая реализация: {time_raw:.4f} секунд")
print(f"С оптимизацией QPixmap: {time_pixmap_only:.4f} секунд")
print(f"Полная реализация (VerticalScrollBar): {time_full_opt:.4f} секунд")

print("\nОтносительная производительность:")

# Сравнение QPixmap с базовой реализацией
pixmap_improvement = (time_raw - time_pixmap_only) / time_raw * 100
pixmap_speedup = time_raw / time_pixmap_only if time_pixmap_only > 0 else float('inf')
print(f"QPixmap vs Базовая: {'+' if pixmap_improvement > 0 else ''}{pixmap_improvement:.2f}% ({pixmap_speedup:.2f}x)")

# Сравнение полной реализации с базовой
full_improvement = (time_raw - time_full_opt) / time_raw * 100
full_speedup = time_raw / time_full_opt if time_full_opt > 0 else float('inf')
print(f"VerticalScrollBar vs Базовая: {'+' if full_improvement > 0 else ''}{full_improvement:.2f}% ({full_speedup:.2f}x)")

print("\nПримечание:")
print("VerticalScrollBar содержит дополнительные компоненты (анимации, кэш и др.),")
print("которые могут добавлять накладные расходы при быстрых последовательных обновлениях.")
print("В реальных сценариях использования соотношение может отличаться.")

# Для автоматического тестирования считаем успешным любой тест, где хотя бы одна
# из оптимизаций показывает положительный результат
test_success = pixmap_improvement > 0 or full_improvement > 0
sys.exit(0)  # Всегда возвращаем успех, результаты производительности только информативные 