# Transparent Scrollbar для PyQt6

Оптимизированная библиотека прозрачных скроллеров для PyQt6 с поддержкой различных визуальных стилей и анимаций.

## Установка

# Из директории с файлом setup.py
```bash
pip install .
```
# Или напрямую из GitHub
```bash
pip install git+https://github.com/ilyashir/transparent-scrollbar-pyqt.git#subdirectory=transparent_scrollbar_pkg
```

## Возможности

- Прозрачные скроллеры с настраиваемым уровнем прозрачности
- Поддержка светлой и темной темы
- Анимация появления/исчезновения скроллеров при наведении мыши
- Кастомизация стилей (цвет, ширина, уровень прозрачности)
- Оптимизированная производительность (кэширование вычислений, минимизация обновлений)

## Использование

### Простой способ (с помощью вспомогательных функций)

```python
from transparent_scrollbar import apply_overlay_scrollbars, toggle_scrollbar_theme

# Создание скроллера со светлой темой
scroll_area = apply_overlay_scrollbars(
    content_widget,
    bg_alpha=10,            # Прозрачность фона
    handle_alpha=100,       # Прозрачность ползунка
    hover_alpha=150,        # Прозрачность при наведении
    pressed_alpha=200,      # Прозрачность при нажатии
    scroll_bar_width=10,    # Ширина скроллеров
    auto_hide=False,        # Автоскрытие скроллеров
    use_dark_theme=False    # Тема оформления
)

# Переключение между темами
toggle_scrollbar_theme(scroll_area, use_dark_theme=True)
```

### Продвинутый способ (прямое использование классов)

```python
from PyQt6.QtWidgets import QScrollArea
from transparent_scrollbar import VerticalScrollBar, HorizontalScrollBar, OverlayScrollArea

# Вариант 1: Создание OverlayScrollArea с настраиваемыми скроллерами
scroll_area = OverlayScrollArea()
scroll_area.setWidget(content_widget)

# Настройка вертикального скроллера
v_scrollbar = scroll_area.verticalScrollBar()
v_scrollbar.set_auto_hide(True)
v_scrollbar.set_use_dark_theme(True)

# Вариант 2: Добавление скроллеров к существующему QScrollArea
scroll_area = QScrollArea()
scroll_area.setWidgetResizable(True)
scroll_area.setWidget(content_widget)

# Замена стандартных скроллеров
v_scrollbar = VerticalScrollBar(auto_hide=True, use_dark_theme=True)
h_scrollbar = HorizontalScrollBar(auto_hide=True, use_dark_theme=True)

scroll_area.setVerticalScrollBar(v_scrollbar)
scroll_area.setHorizontalScrollBar(h_scrollbar)
```

## Оптимизации

В библиотеке реализованы следующие оптимизации для улучшения производительности:

1. Кэширование расчетов положения и размеров ползунка
2. Оптимизация рендеринга с использованием QPixmap
3. Увеличенный интервал обновления таймера
4. Оптимизация анимаций с ленивой инициализацией
5. Оптимизированная обработка событий мыши
6. Ленивое создание графических ресурсов

## Требования

- Python 3.6+
- PyQt6 
