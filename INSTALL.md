# Установка библиотеки Transparent Scrollbar

## Требования

- Python 3.6 или выше
- PyQt6

## Установка из исходного кода

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ilyashir/transparent-scrollbar-pyqt.git
   cd transparent-scrollbar-pyqt
   ```

2. Установите пакет:
   ```bash
   pip install -e transparent_scrollbar_pkg
   ```

## Установка напрямую из GitHub

```bash
pip install git+https://github.com/ilyashir/transparent-scrollbar-pyqt.git#subdirectory=transparent_scrollbar_pkg
```

## Установка из скомпилированного пакета

1. Скачайте последнюю версию пакета из раздела Releases
2. Установите скачанный пакет:
   ```bash
   pip install transparent_scrollbar-X.Y.Z.tar.gz
   ```
   где X.Y.Z - номер версии пакета

## Проверка установки

Для проверки корректности установки запустите тесты:

```bash
python -c "import transparent_scrollbar; print(transparent_scrollbar.__version__)"
```

Если всё установлено правильно, вы увидите номер версии пакета.

## Запуск демо-приложения

Для запуска демонстрационного приложения:

```bash
cd примеры_папка
python main.py
```

## Возможные проблемы

### PyQt6 не установлен

Если вы получаете ошибку при импорте PyQt6, установите этот пакет:

```bash
pip install PyQt6
```

### Конфликты с другими версиями Qt

Если у вас установлены другие версии Qt или PySide, возможны конфликты. В этом случае рекомендуется использовать виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install PyQt6
pip install git+https://github.com/ilyashir/transparent-scrollbar-pyqt.git#subdirectory=transparent_scrollbar_pkg
``` 