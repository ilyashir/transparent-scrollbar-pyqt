# Руководство по содействию проекту

Спасибо за интерес к проекту Transparent Scrollbar для PyQt6! Ниже приведены рекомендации по участию в разработке.

## Как можно внести свой вклад

1. **Сообщение о багах**
   - Используйте систему Issues на GitHub
   - Включайте полное описание проблемы
   - Добавляйте шаги для воспроизведения
   - Укажите версию PyQt6 и Python

2. **Предложение улучшений**
   - Обсуждайте предложения в Issues перед реализацией
   - Описывайте, какую проблему решает улучшение
   - Предлагайте варианты реализации

3. **Отправка кода**
   - Создавайте отдельную ветку для каждой фичи/исправления
   - Следуйте стилю кода проекта
   - Добавляйте тесты для новой функциональности
   - Убедитесь, что все существующие тесты проходят

## Процесс разработки

1. **Форкните репозиторий**
2. **Создайте ветку**: `git checkout -b feature/your-feature-name`
3. **Внесите изменения**
4. **Запустите тесты**: `python tests/run_all_tests.py`
5. **Отправьте Pull Request**

## Стиль кода

- Следуйте PEP 8
- Используйте типизацию (type hints)
- Пишите содержательные docstrings
- Соблюдайте архитектуру проекта

## Тестирование

Все новые функции должны иметь тесты. Запустите все тесты перед отправкой Pull Request:

```bash
python tests/run_all_tests.py
```

## Документация

При добавлении новых функций обновляйте:
- Комментарии в коде
- README.md
- Примеры использования

## Pull Request

- Описывайте изменения четко и понятно
- Указывайте, какую проблему решают изменения
- Ссылайтесь на Issue, если применимо
- Добавьте себя в список авторов, если это ваш первый вклад

## Лицензия

Внося свой вклад, вы соглашаетесь, что ваш код будет лицензирован под [MIT License](LICENSE). 