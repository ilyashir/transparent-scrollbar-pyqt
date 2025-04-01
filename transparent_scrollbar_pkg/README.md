# Прозрачные скроллбары для PyQt6

Библиотека прозрачных, анимированных и настраиваемых скроллбаров для PyQt6.

## Особенности

- Полностью настраиваемые прозрачные скроллбары
- Анимация появления и исчезновения
- Поддержка светлой и темной темы
- Оптимизированный рендеринг для высокой производительности
- Автоматическое скрытие скроллбаров при бездействии
- Поддержка как обычных виджетов (через QScrollArea), так и QGraphicsView

## Установка

```bash
pip install git+https://github.com/ilyashir/transparent-scrollbar-pyqt.git#subdirectory=transparent_scrollbar_pkg
```

## Использование

### Для обычных виджетов

Самый простой способ использования - функция `apply_overlay_scrollbars`:

```python
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from transparent_scrollbar import apply_overlay_scrollbars

app = QApplication([])

# Создаем содержимое
content = QWidget()
layout = QVBoxLayout(content)

# Добавляем много элементов для скроллинга
for i in range(100):
    label = QLabel(f"Элемент {i}")
    layout.addWidget(label)

# Применяем прозрачные скроллбары
scroll_area = apply_overlay_scrollbars(
    content,
    bg_alpha=30,            # Прозрачность фона
    handle_alpha=80,        # Прозрачность ползунка
    hover_alpha=120,        # Прозрачность при наведении
    pressed_alpha=160,      # Прозрачность при нажатии
    scroll_bar_width=8,     # Ширина скроллбаров
    auto_hide=True,         # Автоскрытие скроллбаров
    use_dark_theme=False    # Светлая/темная тема
)

# Отображаем виджет
scroll_area.show()
app.exec()
```

### Для QGraphicsView

Для QGraphicsView используется специальная функция `apply_scrollbars_to_graphics_view`:

```python
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush, QPen
from transparent_scrollbar import apply_scrollbars_to_graphics_view

app = QApplication([])

# Создаем QGraphicsView и QGraphicsScene
view = QGraphicsView()
scene = QGraphicsScene()
view.setScene(scene)

# Настраиваем размер сцены и добавляем элементы
scene.setSceneRect(0, 0, 2000, 2000)
for i in range(10):
    for j in range(10):
        color = QColor.fromHsv(((i * 10 + j) * 15) % 360, 200, 200)
        scene.addRect(i * 200, j * 200, 190, 190, 
                     pen=QPen(Qt.PenStyle.NoPen),
                     brush=QBrush(color))

# Применяем прозрачные скроллбары к QGraphicsView
vsb, hsb = apply_scrollbars_to_graphics_view(
    view,
    bg_alpha=10,          # Прозрачность фона
    handle_alpha=100,     # Прозрачность ползунка
    hover_alpha=150,      # Прозрачность при наведении
    pressed_alpha=200,    # Прозрачность при нажатии
    scroll_bar_width=10,  # Ширина скроллбара
    use_dark_theme=True,  # Темная тема
    auto_hide=True        # Автоскрытие
)

# Отображаем GraphicsView
view.resize(800, 600)
view.show()
app.exec()
```

## Более сложное использование

### Прямое создание скроллбаров

Вы также можете напрямую использовать классы скроллбаров:

```python
from PyQt6.QtWidgets import QApplication, QScrollArea, QLabel
from PyQt6.QtCore import Qt
from transparent_scrollbar import VerticalScrollBar, HorizontalScrollBar

app = QApplication([])

# Создаем QScrollArea
scroll_area = QScrollArea()
scroll_area.setWidget(QLabel("Большой контент"))

# Создаем и настраиваем скроллбары
vsb = VerticalScrollBar()
vsb.bg_alpha = 30
vsb.handle_alpha = 80
vsb.hover_alpha = 120
vsb.pressed_alpha = 160
vsb.auto_hide = True
vsb.use_dark_theme = False

hsb = HorizontalScrollBar()
hsb.bg_alpha = 30
hsb.handle_alpha = 80
hsb.hover_alpha = 120
hsb.pressed_alpha = 160
hsb.auto_hide = True
hsb.use_dark_theme = False

# Устанавливаем скроллбары
scroll_area.setVerticalScrollBar(vsb)
scroll_area.setHorizontalScrollBar(hsb)

scroll_area.resize(400, 300)
scroll_area.show()
app.exec()
```

### Переключение темы

Библиотека поддерживает динамическое переключение между светлой и темной темой:

```python
from transparent_scrollbar import toggle_scrollbar_theme

# ... создаем scroll_area с прозрачными скроллбарами ...

# Переключаем на темную тему
toggle_scrollbar_theme(scroll_area, use_dark_theme=True)

# Переключаем обратно на светлую тему
toggle_scrollbar_theme(scroll_area, use_dark_theme=False)
```

## Архитектура библиотеки

Библиотека имеет модульную архитектуру:

1. `BaseScrollBar` - базовый класс для всех скроллбаров
2. `VerticalScrollBar` и `HorizontalScrollBar` - специализированные скроллбары
3. `OverlayScrollArea` - специальная реализация QScrollArea с поддержкой прозрачных скроллбаров
4. `ScrollBarThemeManager` - менеджер тем для скроллбаров
5. `ScrollBarAnimationManager` - менеджер анимаций для скроллбаров
6. `GraphicsViewScrollBar` - базовый класс для скроллбаров QGraphicsView
7. `GraphicsViewVerticalScrollBar` и `GraphicsViewHorizontalScrollBar` - скроллбары для QGraphicsView

## Оптимизации

Библиотека содержит несколько оптимизаций для улучшения производительности:

1. Кэширование расчетов положения и размеров ползунка
2. Оптимизация рендеринга с использованием QPixmap
3. Увеличенный интервал обновления таймера
4. Оптимизация анимаций с ленивой инициализацией
5. Оптимизированная обработка событий мыши
6. Ленивое создание графических ресурсов

## Требования

- Python 3.6+
- PyQt6 