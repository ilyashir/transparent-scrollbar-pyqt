# Приложение с прозрачными скроллерами

Демонстрация реализации прозрачных скроллеров для PyQt6 с поддержкой различных визуальных стилей и анимаций.

## Возможности

- **Прозрачные скроллеры** с настраиваемым уровнем прозрачности
- **Поддержка светлой и темной темы**
- **Анимация появления/исчезновения** скроллеров при наведении мыши
- **Кастомизация стилей** (цвет, ширина, уровень прозрачности)
- **Оптимизированная производительность** (кэширование вычислений, минимизация обновлений)

## Структура проекта

- `main.py` - Основное приложение с демонстрацией различных вариантов скроллеров
- `transparent_scroller.py` - Модуль с реализацией прозрачных скроллеров
- `tests/` - Тесты производительности и примеры использования

## Использование

```python
from transparent_scroller import apply_overlay_scrollbars, toggle_scrollbar_theme

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

## Оптимизации

Проект включает следующие оптимизации:

1. **Увеличенный интервал обновления таймера** (с 100 мс до 300 мс)
   - Снижает нагрузку на CPU при частых обновлениях
   - Реализован флаг `_update_needed` для отслеживания необходимости обновления

2. **Кэширование расчетов положения и размеров ползунка**
   - Устраняет повторные вычисления при каждой перерисовке
   - Реализован механизм инвалидации кэша при изменении параметров

3. **Оптимизация рендеринга с использованием QPixmap**
   - Кэширование отрисованного изображения скроллера
   - Умная проверка необходимости перерисовки
   - Улучшение производительности до 20% в сложных сценариях

## Тесты производительности

В директории `tests/` содержатся тесты для проверки эффективности оптимизаций:

- `simple_test.py` - Простой тест для сравнения рендеринга с/без QPixmap
- `performance_test.py` - Комплексный тест всех оптимизаций

Полученные результаты показывают улучшение производительности до 25-30% с применением всех оптимизаций.

## Требования

- Python 3.x
- PyQt6

## Запуск

```
python main.py
```

## Лицензия

MIT 