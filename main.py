from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QMainWindow,
                          QHBoxLayout, QScrollArea, QPushButton, QComboBox)
from PyQt6.QtCore import Qt
from transparent_scroller import apply_overlay_scrollbars, toggle_scrollbar_theme, OverlayScrollArea

# Создаем приложение
app = QApplication([])

# Создаем главное окно
window = QMainWindow()
window.setWindowTitle("Сравнение скроллеров - с поддержкой тем")
window.resize(600, 400)  # Увеличиваем ширину для четырех колонок

# Создаем горизонтальный контейнер для колонок
container = QWidget()
h_layout = QHBoxLayout(container)
h_layout.setContentsMargins(10, 10, 10, 10)
h_layout.setSpacing(15)  # Отступ между колонками

# ======== ПЕРВАЯ КОЛОНКА: СТАНДАРТНЫЕ СКРОЛЛБАРЫ ========
# Создаем содержимое
std_content = QWidget()
std_layout = QVBoxLayout(std_content)

# Добавляем заголовок
std_title = QLabel("Стандартные скроллеры")
std_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
std_title.setStyleSheet("font-weight: bold;")
std_layout.addWidget(std_title)

# Добавляем много строк текста для проверки прокрутки
for i in range(50):
    label = QLabel(f"------ Стандартный скроллер: Строка {i + 1}")
    label.setMinimumWidth(100)  # Делаем широкий контент для горизонтальной прокрутки
    std_layout.addWidget(label)

# Используем стандартный QScrollArea
std_scroll_area = QScrollArea()
std_scroll_area.setWidgetResizable(True)
std_scroll_area.setWidget(std_content)

# Добавляем в первую колонку
h_layout.addWidget(std_scroll_area)

# ======== ВТОРАЯ КОЛОНКА: СВЕТЛАЯ ТЕМА (ПОСТОЯННО ВИДИМЫЕ) ========
# Создаем содержимое
light_content = QWidget()
light_layout = QVBoxLayout(light_content)

# Добавляем заголовок
light_title = QLabel("Светлая тема (всегда видимые)")
light_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
light_title.setStyleSheet("font-weight: bold;")
light_layout.addWidget(light_title)

# Добавляем много строк текста для проверки прокрутки
for i in range(50):
    label = QLabel(f"------ Светлая тема: Строка {i + 1}")
    label.setMinimumWidth(200)  # Делаем широкий контент для горизонтальной прокрутки
    light_layout.addWidget(label)

# Применяем прозрачные скроллеры со светлой темой
light_scroll = apply_overlay_scrollbars(
    light_content,
    bg_alpha=10,            # Почти прозрачный фон
    handle_alpha=100,       # Обычное состояние ползунка
    hover_alpha=150,        # При наведении мыши
    pressed_alpha=200,      # При нажатии
    scroll_bar_width=10,    # Ширина скроллеров
    auto_hide=False,        # Отключаем автоскрытие
    use_dark_theme=False    # Используем светлую тему
)

# Добавляем во вторую колонку
h_layout.addWidget(light_scroll)

# ======== ТРЕТЬЯ КОЛОНКА: ТЕМНАЯ ТЕМА (ПОСТОЯННО ВИДИМЫЕ) ========
# Создаем содержимое
dark_content = QWidget()
dark_layout = QVBoxLayout(dark_content)

# Установка темного фона для виджета с темной темой
dark_content.setStyleSheet("background-color: #2D2D30; color: white;")

# Добавляем заголовок
dark_title = QLabel("Темная тема (всегда видимые)")
dark_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
dark_title.setStyleSheet("font-weight: bold; color: white;")
dark_layout.addWidget(dark_title)

# Добавляем много строк текста для проверки прокрутки
for i in range(50):
    label = QLabel(f"------ Темная тема: Строка {i + 1}")
    label.setMinimumWidth(200)  # Делаем широкий контент для горизонтальной прокрутки
    dark_layout.addWidget(label)

# Применяем прозрачные скроллеры с темной темой
dark_scroll = apply_overlay_scrollbars(
    dark_content,
    bg_alpha=10,            # Почти прозрачный фон
    handle_alpha=100,       # Обычное состояние ползунка
    hover_alpha=150,        # При наведении мыши
    pressed_alpha=200,      # При нажатии
    scroll_bar_width=15,    # Ширина скроллеров
    auto_hide=False,        # Отключаем автоскрытие
    use_dark_theme=True     # Используем темную тему
)

# Добавляем в третью колонку
h_layout.addWidget(dark_scroll)

# ======== ЧЕТВЕРТАЯ КОЛОНКА: СКРОЛЛЕРЫ С АНИМАЦИЕЙ И ПЕРЕКЛЮЧАТЕЛЕМ ТЕМ ========
# Создаем виджет с макетом для колонки
theme_switch_widget = QWidget()
theme_switch_layout = QVBoxLayout(theme_switch_widget)
theme_switch_layout.setContentsMargins(0, 0, 0, 0)

# Создаем содержимое с прокруткой
animated_content = QWidget()
animated_layout = QVBoxLayout(animated_content)

# Добавляем заголовок
animated_title = QLabel("Анимированные скроллеры")
animated_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
animated_title.setStyleSheet("font-weight: bold;")
animated_layout.addWidget(animated_title)

# Добавляем инструкцию
instruction = QLabel("Наведите мышь для появления скроллеров")
instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
instruction.setStyleSheet("color: #666; font-style: italic;")
animated_layout.addWidget(instruction)

# Добавляем много строк текста для проверки прокрутки
for i in range(50):
    label = QLabel(f"------ Кастомный скроллер с анимацией: Строка {i + 1}")
    label.setMinimumWidth(100)  # Делаем широкий контент для горизонтальной прокрутки
    animated_layout.addWidget(label)

# Применяем настраиваемые скроллеры с анимацией
animated_scroll = apply_overlay_scrollbars(
    animated_content,
    bg_alpha=5,             # Почти прозрачный фон
    handle_alpha=100,        # Низкая прозрачность в обычном состоянии
    hover_alpha=150,        # Средняя прозрачность при наведении
    pressed_alpha=200,      # Низкая прозрачность при нажатии
    scroll_bar_width=15,    # Ширина скроллеров
    auto_hide=True,         # Включаем автоскрытие с анимацией
    use_dark_theme=False    # По умолчанию светлая тема
)

# Создаем выпадающий список для выбора темы
theme_selector = QComboBox()
theme_selector.addItem("Светлая тема")
theme_selector.addItem("Темная тема")
theme_selector.setStyleSheet("""
    QComboBox {
        padding: 5px;
        border: 1px solid #aaa;
        border-radius: 3px;
        background-color: #f5f5f5;
    }
""")

# Обработчик смены темы
def on_theme_changed(index):
    use_dark_theme = (index == 1)  # 0 - светлая, 1 - темная
    toggle_scrollbar_theme(animated_scroll, use_dark_theme)
    
    # Обновляем стиль инструкции в зависимости от темы
    if use_dark_theme:
        instruction.setStyleSheet("color: #aaa; font-style: italic;")
        animated_content.setStyleSheet("background-color: #2D2D30; color: white;")
    else:
        instruction.setStyleSheet("color: #666; font-style: italic;")
        animated_content.setStyleSheet("background-color: #f5f5f5; color: black;")

# Подключаем обработчик
theme_selector.currentIndexChanged.connect(on_theme_changed)

# Добавляем селектор темы и прокручиваемый контент
theme_switch_layout.addWidget(theme_selector)
theme_switch_layout.addWidget(animated_scroll)

# Добавляем в четвертую колонку
h_layout.addWidget(theme_switch_widget)

# Устанавливаем контейнер как центральный виджет
window.setCentralWidget(container)

# Запускаем приложение
window.show()
app.exec()