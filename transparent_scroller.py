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

class TransparentScroller(QScrollBar):
    """Прозрачный скроллер с настраиваемой прозрачностью"""
    
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
    
    def _invalidateCache(self):
        """Отмечает кэш как устаревший"""
        self._cache_dirty = True
        self._pixmap_cache_dirty = True
        # Сбрасываем кэш промежуточных вычислений
        self._cached_params = None
        self._cached_ratios = None
    
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
        
        if self._orientation == Qt.Orientation.Vertical:
            # Для вертикального скроллбара
            handle_height = max(20, int(height * handle_size_ratio))
            available_height = height - handle_height
            handle_pos = int(available_height * position_ratio)
            
            rect = QRect(
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
            
            rect = QRect(
                handle_pos, 
                margin, 
                handle_width, 
                height - 2 * margin
            )
        
        # Кэшируем результат и сохраняем параметры, при которых он был вычислен
        self._cached_slider_rect = rect
        self._cached_params = (min_val, max_val, page_step, value, width, height)
        self._cache_dirty = False
        return rect
    
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


class OverlayScrollArea(QScrollArea):
    """Класс области прокрутки с накладываемыми пользовательскими скроллбарами"""
    
    def __init__(self, widget, bg_alpha=30, handle_alpha=80, 
                 hover_alpha=120, pressed_alpha=160,
                 scroll_bar_width=8, auto_hide=False, use_dark_theme=False):
        super().__init__()
        
        # Сохраняем параметры
        self._bg_alpha = bg_alpha
        self._handle_alpha = handle_alpha
        self._hover_alpha = hover_alpha
        self._pressed_alpha = pressed_alpha
        self._auto_hide = auto_hide
        self._use_dark_theme = use_dark_theme
        self._scroll_bar_width = scroll_bar_width
        
        # Настройка области прокрутки
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setWidget(widget)
        
        # Скрываем стандартные скроллбары
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Создаем наши пользовательские скроллбары
        self._v_scroll = TransparentScroller(
            Qt.Orientation.Vertical, 
            bg_alpha, handle_alpha, hover_alpha, pressed_alpha,
            scroll_bar_width, use_dark_theme
        )
        self._h_scroll = TransparentScroller(
            Qt.Orientation.Horizontal, 
            bg_alpha, handle_alpha, hover_alpha, pressed_alpha,
            scroll_bar_width, use_dark_theme
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
        
        # Инициализируем анимации
        self._v_anim = None
        self._h_anim = None
        
        # Управление видимостью скроллбаров и анимациями
        if self._auto_hide:
            # Создаем анимации только при необходимости
            self._initAnimations()
            # Начинаем с невидимых скроллбаров
            self._v_scroll.setOpacity(0.0)
            self._h_scroll.setOpacity(0.0)
        else:
            # Если автоскрытие отключено, просто делаем скроллбары видимыми
            self._v_scroll.setOpacity(1.0)
            self._h_scroll.setOpacity(1.0)
        
        # Таймер для редкого обновления состояния скроллбаров (когда нет прокрутки)
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._updateScrollBars)
        self._update_timer.start(300)  # Обновляем каждые 300 мс вместо 100 мс
        
        # Флаг для отслеживания необходимости обновления
        self._update_needed = True
        
        # Обновляем скроллбары сразу после инициализации
        QTimer.singleShot(0, self._updateScrollBars)
    
    def _initAnimations(self):
        """Инициализация и настройка анимаций для скроллбаров"""
        # Создаем анимацию для вертикального скроллбара
        self._v_anim = QPropertyAnimation(self._v_scroll, b"opacity")
        self._v_anim.setEasingCurve(QEasingCurve.Type.OutCubic)  # Более плавная кривая
        
        # Создаем анимацию для горизонтального скроллбара
        self._h_anim = QPropertyAnimation(self._h_scroll, b"opacity")
        self._h_anim.setEasingCurve(QEasingCurve.Type.OutCubic)  # Более плавная кривая
    
    def _setupShowAnimation(self):
        """Настройка анимации появления скроллбаров"""
        # Настраиваем анимации только если они созданы
        if self._v_anim and self._h_anim:
            self._v_anim.setDuration(300)  # Быстрое появление
            self._v_anim.setEndValue(1.0)
            
            self._h_anim.setDuration(300)  # Быстрое появление
            self._h_anim.setEndValue(1.0)
    
    def _setupHideAnimation(self):
        """Настройка анимации скрытия скроллбаров"""
        # Настраиваем анимации только если они созданы
        if self._v_anim and self._h_anim:
            self._v_anim.setDuration(700)  # Медленное исчезновение
            self._v_anim.setEndValue(0.0)
            
            self._h_anim.setDuration(700)  # Медленное исчезновение
            self._h_anim.setEndValue(0.0)
    
    def _startShowAnimation(self):
        """Запуск анимации появления скроллбаров"""
        # Запускаем анимации только если они созданы и нужны
        if self._auto_hide and self._v_anim and self._h_anim:
            # Останавливаем текущие анимации
            self._v_anim.stop()
            self._h_anim.stop()
            
            # Настраиваем анимацию на появление
            self._setupShowAnimation()
            
            # Устанавливаем начальные значения (текущая прозрачность)
            self._v_anim.setStartValue(self._v_scroll._opacity)
            self._h_anim.setStartValue(self._h_scroll._opacity)
            
            # Запускаем анимации
            self._v_anim.start()
            self._h_anim.start()
    
    def _startHideAnimation(self):
        """Запуск анимации скрытия скроллбаров"""
        # Запускаем анимации только если они созданы и нужны
        if self._auto_hide and self._v_anim and self._h_anim:
            # Останавливаем текущие анимации
            self._v_anim.stop()
            self._h_anim.stop()
            
            # Настраиваем анимацию на скрытие
            self._setupHideAnimation()
            
            # Устанавливаем начальные значения (текущая прозрачность)
            self._v_anim.setStartValue(self._v_scroll._opacity)
            self._h_anim.setStartValue(self._h_scroll._opacity)
            
            # Запускаем анимации
            self._v_anim.start()
            self._h_anim.start()
    
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
        
        # Если автоскрытие включено, показываем скроллбары
        if self._auto_hide:
            # Настраиваем анимацию появления
            self._setupShowAnimation()
            # Запускаем анимацию
            self._startShowAnimation()
    
    def leaveEvent(self, event):
        """Обработка выхода курсора за пределы виджета"""
        super().leaveEvent(event)
        
        # Если автоскрытие включено, скрываем скроллбары
        if self._auto_hide:
            # Настраиваем анимацию исчезновения
            self._setupHideAnimation()
            # Запускаем анимацию
            self._startHideAnimation()


def apply_overlay_scrollbars(widget, bg_alpha=30, handle_alpha=80, 
                             hover_alpha=120, pressed_alpha=160,
                             scroll_bar_width=8, auto_hide=False,
                             use_dark_theme=False):
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
    
    Returns:
        OverlayScrollArea: Область прокрутки с настроенными скроллбарами
    """
    # Создаем область прокрутки с настраиваемыми скроллбарами
    scroll_area = OverlayScrollArea(
        widget, bg_alpha, handle_alpha, 
        hover_alpha, pressed_alpha, scroll_bar_width,
        auto_hide, use_dark_theme
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