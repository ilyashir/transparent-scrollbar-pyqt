from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QFrame, QScrollBar, QApplication, QHBoxLayout)
from PyQt6.QtCore import Qt, QRect, QPoint, QTimer, QEvent, QObject, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPen, QPaintEvent, QPixmap

# Предопределенные цвета для тем
LIGHT_THEME = {
    "bg_color": QColor(200, 200, 200),
    "handle_color": QColor(150, 150, 150),
    "hover_color": QColor(80, 80, 80),       # Гораздо темнее обычного
    "pressed_color": QColor(40, 40, 40)      # Еще темнее
}

DARK_THEME = {
    "bg_color": QColor(80, 80, 80),
    "handle_color": QColor(120, 120, 120),
    "hover_color": QColor(200, 200, 200),    # Гораздо светлее обычного
    "pressed_color": QColor(240, 240, 240)   # Еще светлее
}


class ScrollBarThemeManager:
    """Класс для управления темами скроллбаров"""
    
    @staticmethod
    def get_theme_colors(use_dark_theme=False):
        """Возвращает цвета для выбранной темы"""
        return DARK_THEME if use_dark_theme else LIGHT_THEME
    
    @staticmethod
    def apply_theme(scrollbar, use_dark_theme=False):
        """Применяет тему к скроллбару"""
        if hasattr(scrollbar, 'setTheme'):
            scrollbar.setTheme(use_dark_theme)


class BaseScrollBar(QScrollBar):
    """Базовый класс для прозрачных скроллбаров с общей функциональностью"""
    
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
        self._configure_size(scroll_bar_width)
        
        # Отслеживаем положение мыши
        self.setMouseTracking(True)
        
        # Инициализируем цвета
        self._initColors()
        
        # Кэширование расчётов ползунка
        self._cached_slider_rect = None
        self._cache_dirty = True
        
        # Кэширование параметров для промежуточных расчетов
        self._cached_params = None  # Кэш параметров (min, max, page_step, value)
        self._cached_ratios = None  # Кэш соотношений (handle_size_ratio, position_ratio)
        
        # Статистика использования кэша
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Соединяем сигналы, которые влияют на геометрию ползунка
        self.valueChanged.connect(self._invalidateCache)
        self.rangeChanged.connect(self._invalidateCache)
        
        # Кэширование рендеринга
        self._pixmap_cache = None
        self._pixmap_cache_dirty = True
        self._last_state = None
    
    def _configure_size(self, scroll_bar_width):
        """Настраивает размер скроллбара в зависимости от ориентации"""
        if self._orientation == Qt.Orientation.Vertical:
            self.setFixedWidth(scroll_bar_width)
        else:
            self.setFixedHeight(scroll_bar_width)
    
    def _invalidateCache(self):
        """Отмечает кэш как устаревший"""
        self._cache_dirty = True
        self._pixmap_cache_dirty = True
        # Сбрасываем кэш промежуточных вычислений
        self._cached_params = None
        self._cached_ratios = None
    
    def _initColors(self):
        """Инициализирует цвета скроллбара на основе темы"""
        theme = ScrollBarThemeManager.get_theme_colors(self.use_dark_theme)
        
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
        
        # Инвалидируем кэш пиксмапа при изменении цветов
        self._pixmap_cache_dirty = True
    
    def setTheme(self, use_dark_theme):
        """Изменение темы скроллбара"""
        self.use_dark_theme = use_dark_theme
        self._initColors()
        self.update()
    
    def opacity(self):
        """Геттер для свойства прозрачности"""
        return self._opacity
    
    def setOpacity(self, opacity):
        """Установка прозрачности скроллбара (0.0 - 1.0)"""
        self._opacity = max(0.0, min(1.0, opacity))
        self.update()
    
    # Определяем свойство для анимации
    opacity = pyqtProperty(float, opacity, setOpacity)
    
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
    
    def paintEvent(self, event):
        """Отрисовка скроллбара с кастомным стилем"""
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
    
    def _calculateSliderRect(self):
        """Вычисляет прямоугольник ползунка скроллбара"""
        # Проверяем, можно ли использовать кэшированное значение
        # Быстрая проверка без обращения к более сложным данным
        if not self._cache_dirty and self._cached_slider_rect is not None:
            self._cache_hits += 1
            return self._cached_slider_rect
        
        # Если дошли до этой точки, значит нужно пересчитать
        self._cache_misses += 1
        
        # Получаем основные параметры скроллбара эффективным способом
        # (значения сразу, без получения их через методы)
        min_val = self.minimum()
        max_val = self.maximum()
        page_step = self.pageStep()
        value = self.value()
        width = self.width()
        height = self.height()
        
        # Если нет диапазона для прокрутки, занимаем всю доступную область
        if max_val <= min_val:
            rect = self.rect().adjusted(2, 2, -2, -2)
            self._cached_slider_rect = rect
            self._cache_dirty = False
            self._cached_params = (min_val, max_val, page_step, value, width, height)
            return rect
        
        # Вычисляем размер ползунка в процентах от общего размера скроллбара
        handle_size_ratio = min(1.0, page_step / (max_val - min_val + page_step))
        
        # Вычисляем положение ползунка в процентах
        position_ratio = (value - min_val) / (max_val - min_val)
        
        # Оптимизация: сохраняем эти соотношения для повторного использования
        self._cached_ratios = (handle_size_ratio, position_ratio)
        
        # Отступы от краев (для эстетики)
        margin = 2
        
        # Получаем прямоугольник в зависимости от ориентации
        rect = self._calculateOrientedRect(handle_size_ratio, position_ratio, margin, width, height)
        
        # Кэшируем результат и сохраняем параметры, при которых он был вычислен
        self._cached_slider_rect = rect
        self._cached_params = (min_val, max_val, page_step, value, width, height)
        self._cache_dirty = False
        return rect
    
    def _calculateOrientedRect(self, handle_size_ratio, position_ratio, margin, width, height):
        """Вычисляет прямоугольник ползунка с учетом ориентации"""
        # Этот метод должен быть переопределен в наследниках
        raise NotImplementedError("Метод _calculateOrientedRect должен быть реализован в наследниках")
    
    def getCacheStats(self):
        """Возвращает статистику использования кэша"""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "total": total,
            "hit_rate": hit_rate
        }
    
    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        super().mousePressEvent(event)
        self._mouse_pressed = True
        self._pixmap_cache_dirty = True  # Инвалидируем кэш
        self.update()
    
    def mouseReleaseEvent(self, event):
        """Обработка отпускания кнопки мыши"""
        super().mouseReleaseEvent(event)
        self._mouse_pressed = False
        self._pixmap_cache_dirty = True  # Инвалидируем кэш
        self.update()
    
    def mouseMoveEvent(self, event):
        """Обработка движения мыши"""
        super().mouseMoveEvent(event)
        
        # Проверяем, находится ли курсор над ползунком
        handle_rect = self._calculateSliderRect()
        was_over = self._mouse_over
        self._mouse_over = handle_rect.contains(event.pos())
        
        # Если состояние изменилось, перерисовываем
        if was_over != self._mouse_over:
            self._pixmap_cache_dirty = True  # Инвалидируем кэш
            self.update()
    
    def enterEvent(self, event):
        """Обработка входа курсора в область виджета"""
        super().enterEvent(event)
        # При входе курсора мыши инвалидируем кэш, так как может измениться состояние
        self._pixmap_cache_dirty = True
    
    def leaveEvent(self, event):
        """Обработка выхода курсора из области виджета"""
        super().leaveEvent(event)
        self._mouse_over = False
        self._pixmap_cache_dirty = True  # Инвалидируем кэш
        self.update()
    
    def resizeEvent(self, event):
        """Обработка изменения размера"""
        super().resizeEvent(event)
        # Инвалидируем кэш при изменении размера
        self._invalidateCache()


class ScrollBarAnimationManager:
    """Класс для управления анимациями скроллбаров"""
    
    def __init__(self, scroll_bar, auto_hide=True, show_duration=300, hide_duration=1000, hide_delay=1000):
        self.scroll_bar = scroll_bar
        self.auto_hide = auto_hide
        self.show_duration = show_duration
        self.hide_duration = hide_duration
        self.hide_delay = hide_delay
        
        # Анимации
        self.show_animation = None
        self.hide_animation = None
        self.hide_timer = None
        
        # Инициализируем анимации только если нужно auto_hide
        if self.auto_hide:
            self._setup_animations()
            self._setup_hide_timer()
            # Начальное состояние - скрытый скроллбар
            self.scroll_bar.setOpacity(0.0)
    
    def _setup_animations(self):
        """Настройка анимаций для показа и скрытия скроллбара"""
        # Анимация показа
        self._setup_show_animation()
        
        # Анимация скрытия
        self._setup_hide_animation()
    
    def _setup_show_animation(self):
        """Настройка анимации показа скроллбара"""
        self.show_animation = QPropertyAnimation(self.scroll_bar, b"opacity")
        self.show_animation.setDuration(self.show_duration)
        self.show_animation.setStartValue(0.0)
        self.show_animation.setEndValue(1.0)
        # Более быстрое начало анимации
        self.show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _setup_hide_animation(self):
        """Настройка анимации скрытия скроллбара"""
        self.hide_animation = QPropertyAnimation(self.scroll_bar, b"opacity")
        self.hide_animation.setDuration(self.hide_duration)
        self.hide_animation.setStartValue(1.0)
        self.hide_animation.setEndValue(0.0)
        # Более плавное начало анимации и быстрый конец
        self.hide_animation.setEasingCurve(QEasingCurve.Type.InCubic)
    
    def _setup_hide_timer(self):
        """Настройка таймера для скрытия скроллбара"""
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.start_hide_animation)
    
    def start_show_animation(self):
        """Запускает анимацию показа скроллбара"""
        if not self.auto_hide:
            return
            
        # Останавливаем таймер и анимацию скрытия, если они активны
        if self.hide_timer.isActive():
            self.hide_timer.stop()
        
        if self.hide_animation and self.hide_animation.state() == QPropertyAnimation.State.Running:
            self.hide_animation.stop()
        
        # Запускаем анимацию показа только если скроллбар не виден полностью
        current_opacity = self.scroll_bar._opacity
        if current_opacity < 1.0:
            self.show_animation.setStartValue(current_opacity)
            self.show_animation.start()
    
    def start_hide_animation(self):
        """Запускает анимацию скрытия скроллбара после задержки"""
        if not self.auto_hide:
            return
            
        # Запускаем анимацию скрытия только если скроллбар виден
        current_opacity = self.scroll_bar._opacity
        if current_opacity > 0.0:
            self.hide_animation.setStartValue(current_opacity)
            self.hide_animation.start()
    
    def restart_hide_timer(self):
        """Перезапускает таймер для скрытия скроллбара"""
        if not self.auto_hide:
            return
            
        # Останавливаем предыдущий таймер, если он был активен
        if self.hide_timer.isActive():
            self.hide_timer.stop()
        
        # Запускаем таймер заново
        self.hide_timer.start(self.hide_delay)
    
    def handle_widget_event(self, event_type):
        """Обрабатывает события виджета для анимации скроллбара"""
        if not self.auto_hide:
            return
            
        if event_type == "enter":
            # При входе курсора показываем скроллбар
            self.start_show_animation()
        elif event_type == "leave":
            # При выходе курсора запускаем таймер для скрытия
            self.restart_hide_timer()
        elif event_type == "scroll":
            # При прокрутке показываем скроллбар и перезапускаем таймер
            self.start_show_animation()
            self.restart_hide_timer()


class VerticalScrollBar(BaseScrollBar):
    """Вертикальный прозрачный скроллбар"""
    
    def __init__(self, bg_alpha=30, handle_alpha=80, hover_alpha=120, pressed_alpha=160,
                 scroll_bar_width=8, use_dark_theme=False, auto_hide=True,
                 show_duration=300, hide_duration=1000, hide_delay=1000):
        super().__init__(Qt.Orientation.Vertical, bg_alpha, handle_alpha, 
                          hover_alpha, pressed_alpha, scroll_bar_width, use_dark_theme)
        
        # Создаем менеджер анимаций
        self.animation_manager = ScrollBarAnimationManager(
            self, auto_hide, show_duration, hide_duration, hide_delay
        )
    
    def _calculateOrientedRect(self, handle_size_ratio, position_ratio, margin, width, height):
        """Вычисляет прямоугольник ползунка для вертикального скроллбара"""
        # Вычисляем размер ползунка
        handle_height = max(width, int((height - 2 * margin) * handle_size_ratio))
        
        # Вычисляем максимальное перемещение ползунка
        max_y = height - handle_height - 2 * margin
        
        # Вычисляем положение ползунка
        handle_y = margin + int(max_y * position_ratio)
        
        # Создаем прямоугольник для ползунка
        return QRect(margin, handle_y, width - 2 * margin, handle_height)
    
    def handle_widget_event(self, event_type):
        """Обрабатывает события виджета для анимации"""
        self.animation_manager.handle_widget_event(event_type)


class HorizontalScrollBar(BaseScrollBar):
    """Горизонтальный прозрачный скроллбар"""
    
    def __init__(self, bg_alpha=30, handle_alpha=80, hover_alpha=120, pressed_alpha=160,
                 scroll_bar_width=8, use_dark_theme=False, auto_hide=True,
                 show_duration=300, hide_duration=1000, hide_delay=1000):
        super().__init__(Qt.Orientation.Horizontal, bg_alpha, handle_alpha, 
                          hover_alpha, pressed_alpha, scroll_bar_width, use_dark_theme)
        
        # Создаем менеджер анимаций
        self.animation_manager = ScrollBarAnimationManager(
            self, auto_hide, show_duration, hide_duration, hide_delay
        )
    
    def _calculateOrientedRect(self, handle_size_ratio, position_ratio, margin, width, height):
        """Вычисляет прямоугольник ползунка для горизонтального скроллбара"""
        # Вычисляем размер ползунка
        handle_width = max(height, int((width - 2 * margin) * handle_size_ratio))
        
        # Вычисляем максимальное перемещение ползунка
        max_x = width - handle_width - 2 * margin
        
        # Вычисляем положение ползунка
        handle_x = margin + int(max_x * position_ratio)
        
        # Создаем прямоугольник для ползунка
        return QRect(handle_x, margin, handle_width, height - 2 * margin)
    
    def handle_widget_event(self, event_type):
        """Обрабатывает события виджета для анимации"""
        self.animation_manager.handle_widget_event(event_type)


class OverlayScrollArea(QScrollArea):
    """Класс области прокрутки с накладываемыми пользовательскими скроллбарами"""
    
    def __init__(self, widget, bg_alpha=30, handle_alpha=80, 
                 hover_alpha=120, pressed_alpha=160,
                 scroll_bar_width=8, auto_hide=False, use_dark_theme=False,
                 show_duration=300, hide_duration=1000, hide_delay=1000):
        super().__init__()
        
        # Сохраняем параметры
        self._bg_alpha = bg_alpha
        self._handle_alpha = handle_alpha
        self._hover_alpha = hover_alpha
        self._pressed_alpha = pressed_alpha
        self._auto_hide = auto_hide
        self._use_dark_theme = use_dark_theme
        self._scroll_bar_width = scroll_bar_width
        self._show_duration = show_duration
        self._hide_duration = hide_duration
        self._hide_delay = hide_delay
        
        # Настройка области прокрутки
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setWidget(widget)
        
        # Скрываем стандартные скроллбары
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Создаем специализированные скроллбары с использованием новых классов
        self._v_scroll = VerticalScrollBar(
            bg_alpha, handle_alpha, hover_alpha, pressed_alpha,
            scroll_bar_width, use_dark_theme, auto_hide,
            show_duration, hide_duration, hide_delay
        )
        
        self._h_scroll = HorizontalScrollBar(
            bg_alpha, handle_alpha, hover_alpha, pressed_alpha,
            scroll_bar_width, use_dark_theme, auto_hide,
            show_duration, hide_duration, hide_delay
        )
        
        # Делаем скроллбары дочерними элементами этого виджета
        self._v_scroll.setParent(self)
        self._h_scroll.setParent(self)
        
        # Устанавливаем начальное положение скроллбаров
        self._v_scroll.move(self.width() - scroll_bar_width, 0)
        self._h_scroll.move(0, self.height() - scroll_bar_width)
        
        # Привязываем сигналы пользовательских скроллбаров к событиям прокрутки
        self._v_scroll.valueChanged.connect(self._scrollValueChanged)
        self._h_scroll.valueChanged.connect(self._scrollValueChanged)
        
        # Привязываем сигналы стандартных скроллбаров к обновлениям
        self.verticalScrollBar().valueChanged.connect(self._updateScrollBars)
        self.horizontalScrollBar().valueChanged.connect(self._updateScrollBars)
        
        # Таймер для редкого обновления состояния скроллбаров (когда нет прокрутки)
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._updateScrollBars)
        self._update_timer.start(300)  # Обновляем каждые 300 мс вместо 100 мс
        
        # Флаг для отслеживания необходимости обновления
        self._update_needed = True
        
        # Обновляем скроллбары сразу после инициализации
        QTimer.singleShot(0, self._updateScrollBars)
    
    def setTheme(self, use_dark_theme):
        """Установка темы для всех скроллбаров"""
        self._use_dark_theme = use_dark_theme
        self._v_scroll.setTheme(use_dark_theme)
        self._h_scroll.setTheme(use_dark_theme)
    
    def _scrollValueChanged(self, value):
        """Обработка изменения значения скроллбара"""
        sender = self.sender()
        
        if sender == self._v_scroll:
            self.verticalScrollBar().setValue(value)
        elif sender == self._h_scroll:
            self.horizontalScrollBar().setValue(value)
        
        # Пометка, что требуется обновление
        self._update_needed = True
        
        # Уведомляем скроллбары о событии прокрутки
        self._v_scroll.handle_widget_event("scroll")
        self._h_scroll.handle_widget_event("scroll")
    
    def resizeEvent(self, event):
        """Обработка изменения размера области прокрутки"""
        super().resizeEvent(event)
        
        # При изменении размера требуется обновление
        self._update_needed = True
        
        # Обновляем положение и размеры скроллбаров
        self._updateScrollBarsGeometry()
    
    def showEvent(self, event):
        """Обработка показа виджета"""
        super().showEvent(event)
        # Обновляем скроллбары при отображении
        self._update_needed = True
        self._updateScrollBars()
    
    def _updateScrollBars(self):
        """Обновляет параметры и состояние скроллбаров"""
        # Проверяем, нужно ли обновление
        v_bar = self.verticalScrollBar()
        h_bar = self.horizontalScrollBar()
        
        # Проверка на изменение размеров или значений скроллбаров
        v_visible = v_bar.maximum() > v_bar.minimum()
        h_visible = h_bar.maximum() > h_bar.minimum()
        
        # Проверка на изменение видимости скроллбаров
        v_visibility_changed = v_visible != self._v_scroll.isVisible()
        h_visibility_changed = h_visible != self._h_scroll.isVisible()
        
        # Проверка на изменение значений скроллбаров
        v_value_changed = self._v_scroll.value() != v_bar.value()
        h_value_changed = self._h_scroll.value() != h_bar.value()
        
        # Выполняем обновление только если что-то изменилось
        if (self._update_needed or v_visibility_changed or h_visibility_changed 
            or v_value_changed or h_value_changed):
            
            # Обновляем диапазоны скроллбаров
            self._v_scroll.setRange(v_bar.minimum(), v_bar.maximum())
            self._v_scroll.setPageStep(v_bar.pageStep())
            self._v_scroll.setSingleStep(v_bar.singleStep())
            self._v_scroll.setValue(v_bar.value())
            
            self._h_scroll.setRange(h_bar.minimum(), h_bar.maximum())
            self._h_scroll.setPageStep(h_bar.pageStep())
            self._h_scroll.setSingleStep(h_bar.singleStep())
            self._h_scroll.setValue(h_bar.value())
            
            # Обновляем видимость скроллбаров
            self._v_scroll.setVisible(v_visible)
            self._h_scroll.setVisible(h_visible)
            
            # Обновляем положение и размеры скроллбаров
            self._updateScrollBarsGeometry()
            
            # Сбрасываем флаг необходимости обновления
            self._update_needed = False
    
    def _updateScrollBarsGeometry(self):
        """Обновляет геометрию скроллбаров"""
        # Вычисляем размеры с учетом видимости обоих скроллбаров
        scrollbar_thickness = self._scroll_bar_width
        
        # Определяем, видны ли скроллбары
        v_visible = self._v_scroll.isVisible()
        h_visible = self._h_scroll.isVisible()
        
        # Получаем размеры области прокрутки
        width = self.width()
        height = self.height()
        
        # Рассчитываем размеры скроллбаров
        v_height = height - (scrollbar_thickness if h_visible else 0)
        h_width = width - (scrollbar_thickness if v_visible else 0)
        
        # Устанавливаем положение и размеры вертикального скроллбара
        self._v_scroll.setGeometry(
            width - scrollbar_thickness,
            0,
            scrollbar_thickness,
            v_height
        )
        
        # Устанавливаем положение и размеры горизонтального скроллбара
        self._h_scroll.setGeometry(
            0,
            height - scrollbar_thickness,
            h_width,
            scrollbar_thickness
        )
    
    def wheelEvent(self, event):
        """Обработка события колесика мыши"""
        # Прокручиваем содержимое
        super().wheelEvent(event)
        
        # Обновляем отображение скроллбаров
        self._update_needed = True
        self._updateScrollBars()
    
    def enterEvent(self, event):
        """Обработка входа курсора в область виджета"""
        super().enterEvent(event)
        
        # Уведомляем скроллбары о событии входа курсора
        self._v_scroll.handle_widget_event("enter")
        self._h_scroll.handle_widget_event("enter")
    
    def leaveEvent(self, event):
        """Обработка выхода курсора за пределы виджета"""
        super().leaveEvent(event)
        
        # Уведомляем скроллбары о событии выхода курсора
        self._v_scroll.handle_widget_event("leave")
        self._h_scroll.handle_widget_event("leave")


def apply_overlay_scrollbars(widget, bg_alpha=30, handle_alpha=80, 
                             hover_alpha=120, pressed_alpha=160,
                             scroll_bar_width=8, auto_hide=False,
                             use_dark_theme=False,
                             show_duration=300, hide_duration=1000, hide_delay=1000):
    """
    Применяет настраиваемые прозрачные скроллбары к виджету
    
    Args:
        widget: Виджет, к которому применяются скроллбары
        bg_alpha: Прозрачность фона скроллбара (0-255)
        handle_alpha: Прозрачность ползунка в обычном состоянии (0-255)
        hover_alpha: Прозрачность ползунка при наведении мыши (0-255)
        pressed_alpha: Прозрачность ползунка при нажатии (0-255)
        scroll_bar_width: Ширина скроллбаров в пикселях
        auto_hide: Включает автоскрытие скроллбаров с анимацией
        use_dark_theme: Использовать темную тему для скроллбаров
        show_duration: Длительность анимации появления (мс)
        hide_duration: Длительность анимации исчезновения (мс)
        hide_delay: Задержка перед скрытием скроллбаров (мс)
    
    Returns:
        OverlayScrollArea: Область прокрутки с настроенными скроллбарами
    """
    # Создаем область прокрутки с настраиваемыми скроллбарами
    scroll_area = OverlayScrollArea(
        widget, bg_alpha, handle_alpha, 
        hover_alpha, pressed_alpha, scroll_bar_width,
        auto_hide, use_dark_theme,
        show_duration, hide_duration, hide_delay
    )
    
    return scroll_area


def toggle_scrollbar_theme(overlay_scroll_area, use_dark_theme):
    """
    Переключает тему скроллбаров между светлой и темной
    
    Args:
        overlay_scroll_area: Экземпляр OverlayScrollArea, тему которого нужно изменить
        use_dark_theme: True для темной темы, False для светлой
    """
    if isinstance(overlay_scroll_area, OverlayScrollArea):
        overlay_scroll_area.setTheme(use_dark_theme)
    else:
        print("Ошибка: аргумент не является экземпляром OverlayScrollArea") 