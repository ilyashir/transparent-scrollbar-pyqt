#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout, QLabel, QScrollArea, QGraphicsView, 
                            QGraphicsScene, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPalette, QColor, QFont, QBrush, QPen

from transparent_scroller import (apply_overlay_scrollbars, toggle_scrollbar_theme, 
                                VerticalScrollBar, HorizontalScrollBar, OverlayScrollArea)
from graphics_view_scroller import apply_scrollbars_to_graphics_view

class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Демо прозрачных скроллбаров")
        self.resize(400, 600)
        
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        self.tab_widget.addTab(self.create_helper_tab(), "Функция-помощник")
        self.tab_widget.addTab(self.create_direct_tab(), "Прямое создание")
        self.tab_widget.addTab(self.create_theme_tab(), "Переключение темы")
        self.tab_widget.addTab(self.create_graphics_view_tab(), "QGraphicsView")
        
    def create_helper_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Создаем много элементов для скроллинга
        for i in range(100):
            label = QLabel(f"Элемент списка #{i}")
            label.setFont(QFont("Arial", 12))
            content_layout.addWidget(label)
        
        # Применяем прозрачные скроллбары с помощью функции-помощника
        scroll_area = apply_overlay_scrollbars(
            content,
            bg_alpha=30,
            handle_alpha=80,
            hover_alpha=120,
            pressed_alpha=160,
            scroll_bar_width=8,
            auto_hide=True,
            use_dark_theme=False
        )
        
        layout.addWidget(QLabel("Использование функции apply_overlay_scrollbars:"))
        layout.addWidget(scroll_area)
        
        return tab
    
    def create_direct_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Создаем много элементов для скроллинга
        for i in range(100):
            label = QLabel(f"Прямое создание - элемент #{i}")
            label.setFont(QFont("Arial", 12))
            content_layout.addWidget(label)
        
        # Создаем QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content)
        
        # Создаем и настраиваем скроллбары
        vsb = VerticalScrollBar()
        vsb.scroll_bar_width = 15
        vsb.bg_alpha = 10
        vsb.handle_alpha = 100
        vsb.hover_alpha = 150
        vsb.pressed_alpha = 200
        vsb.auto_hide = True
        vsb.use_dark_theme = False
        
        hsb = HorizontalScrollBar()
        hsb.scroll_bar_width = 15
        hsb.bg_alpha = 10
        hsb.handle_alpha = 100
        hsb.hover_alpha = 150
        hsb.pressed_alpha = 200
        hsb.auto_hide = True
        hsb.use_dark_theme = False
        
        # Устанавливаем скроллбары
        scroll_area.setVerticalScrollBar(vsb)
        scroll_area.setHorizontalScrollBar(hsb)
        
        layout.addWidget(QLabel("Прямое создание и настройка скроллбаров:"))
        layout.addWidget(scroll_area)
        
        return tab
    
    def create_theme_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Создаем много элементов для скроллинга
        for i in range(100):
            label = QLabel(f"Тема - элемент #{i}")
            label.setFont(QFont("Arial", 12))
            content_layout.addWidget(label)
        
        # Применяем прозрачные скроллбары
        self.theme_scroll_area = apply_overlay_scrollbars(
            content,
            bg_alpha=20,
            handle_alpha=70,
            hover_alpha=130,
            pressed_alpha=180,
            scroll_bar_width=20,
            auto_hide=True,
            use_dark_theme=False
        )
        
        # Добавляем кнопку для переключения темы
        theme_btn = QLabel("Нажмите здесь для переключения темы")
        theme_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        theme_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        theme_btn.setStyleSheet("background-color: #e0e0e0; padding: 10px; border-radius: 5px;")
        theme_btn.mousePressEvent = self.toggle_theme
        
        # Добавляем кнопки для изменения размера контента
        size_controls = QWidget()
        size_layout = QVBoxLayout(size_controls)
        
        # Кнопка для добавления/удаления элементов по вертикали
        height_btn = QLabel("Нажмите для изменения высоты контента")
        height_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        height_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        height_btn.setStyleSheet("background-color: #e0e0e0; padding: 10px; border-radius: 5px;")
        height_btn.mousePressEvent = self.toggle_content_height
        height_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Кнопка для добавления/удаления элементов по горизонтали
        width_btn = QLabel("Нажмите для изменения ширины контента")
        width_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        width_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        width_btn.setStyleSheet("background-color: #e0e0e0; padding: 10px; border-radius: 5px;")
        width_btn.mousePressEvent = self.toggle_content_width
        width_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        size_layout.addWidget(height_btn)
        size_layout.addWidget(width_btn)
        
        layout.addWidget(theme_btn)
        layout.addWidget(size_controls)
        layout.addWidget(self.theme_scroll_area)
        
        # Сохраняем ссылки на элементы для управления
        self.theme_content = content
        self.theme_content_layout = content_layout
        self._is_tall_content = True
        self._is_wide_content = True
        
        return tab
    
    def toggle_theme(self, event):
        # Инвертируем текущую тему
        is_dark = self.theme_scroll_area.property("using_dark_theme")
        new_theme = not is_dark if is_dark is not None else True
        
        # Применяем новую тему к скроллбарам
        toggle_scrollbar_theme(self.theme_scroll_area, new_theme)
        
        # Сохраняем информацию о текущей теме
        self.theme_scroll_area.setProperty("using_dark_theme", new_theme)
        
        # Изменяем фон окна
        bg_color = QColor(30, 30, 30) if new_theme else QColor(240, 240, 240)
        self.theme_scroll_area.setStyleSheet(f"background-color: {bg_color.name()};")
        # Обновляем цвет текста для лучшей читаемости
        text_color = "white" if new_theme else "black"
        for i in range(self.theme_scroll_area.widget().layout().count()):
            label = self.theme_scroll_area.widget().layout().itemAt(i).widget()
            if isinstance(label, QLabel):
                label.setStyleSheet(f"color: {text_color};")
        
    def toggle_content_height(self, event):
        """Переключение высоты контента"""
        self._is_tall_content = not self._is_tall_content
        
        # Очищаем текущий контент
        while self.theme_content_layout.count():
            item = self.theme_content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Добавляем новый контент
        count = 200 if self._is_tall_content else 15
        for i in range(count):
            label = QLabel(f"Тема - элемент #{i}")
            label.setFont(QFont("Arial", 12))
            self.theme_content_layout.addWidget(label)
        
        # Обновляем стили для всех лейблов
        is_dark = self.theme_scroll_area.property("using_dark_theme")
        text_color = "white" if is_dark else "black"
        for i in range(self.theme_content_layout.count()):
            label = self.theme_content_layout.itemAt(i).widget()
            if isinstance(label, QLabel):
                label.setStyleSheet(f"color: {text_color};")
    
    def toggle_content_width(self, event):
        """Переключение ширины контента"""
        self._is_wide_content = not self._is_wide_content
        
        # Очищаем текущий контент
        while self.theme_content_layout.count():
            item = self.theme_content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Добавляем новый контент с разной шириной
        count = 50
        for i in range(count):
            label = QLabel(f"Тема - элемент #{i} " + ("x" * 100 if self._is_wide_content else ""))
            label.setFont(QFont("Arial", 12))
            label.setWordWrap(True)
            self.theme_content_layout.addWidget(label)
        
        # Обновляем стили для всех лейблов
        is_dark = self.theme_scroll_area.property("using_dark_theme")
        text_color = "white" if is_dark else "black"
        for i in range(self.theme_content_layout.count()):
            label = self.theme_content_layout.itemAt(i).widget()
            if isinstance(label, QLabel):
                label.setStyleSheet(f"color: {text_color};")
    
    def create_graphics_view_tab(self):
        """Создает вкладку с демонстрацией QGraphicsView."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Создаем QGraphicsView
        graphics_view = QGraphicsView()
        scene = QGraphicsScene()
        graphics_view.setScene(scene)
        
        # Настраиваем размер сцены (намного больше, чем размер просмотра)
        scene.setSceneRect(0, 0, 2000, 2000)
        
        # Сохраняем ссылки для управления
        self.graphics_scene = scene
        self._is_large_grid = True
        
        # Добавляем элементы на сцену (прямоугольники со светлой заливкой и темной границей)
        self._add_rectangles_to_scene()
        
        # Применяем прозрачные скроллбары к QGraphicsView
        vsb, hsb = apply_scrollbars_to_graphics_view(
            graphics_view,
            bg_alpha=10,
            handle_alpha=100,
            hover_alpha=150,
            pressed_alpha=200,
            scroll_bar_width=15,
            use_dark_theme=True,
            auto_hide=True
        )
        
        # Добавляем кнопку для изменения размера сетки
        grid_btn = QLabel("Нажмите для изменения размера сетки")
        grid_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        grid_btn.setStyleSheet("background-color: #e0e0e0; padding: 10px; border-radius: 5px;")
        grid_btn.mousePressEvent = self.toggle_grid_size
        grid_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        description = QLabel(
            "Демонстрация прозрачных скроллбаров для QGraphicsView.\n"
            "Скроллбары появляются при наведении на область просмотра и автоматически скрываются."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setFont(QFont("Arial", 11))
        
        layout.addWidget(description)
        layout.addWidget(grid_btn)
        layout.addWidget(graphics_view)
        
        return tab
    
    def _add_rectangles_to_scene(self):
        """Добавляет прямоугольники на сцену"""
        # Очищаем сцену
        self.graphics_scene.clear()
        
        # Определяем размер сетки
        grid_size = 10 if self._is_large_grid else 2
        
        # Изменяем размер сцены в зависимости от размера сетки
        scene_size = grid_size * 200  # 200 - размер ячейки (190 + 10 отступ)
        self.graphics_scene.setSceneRect(0, 0, scene_size, scene_size)
        
        # Добавляем элементы на сцену
        for i in range(grid_size):
            for j in range(grid_size):
                # Создаем светлый цвет для заливки
                fill_color = QColor(240, 240, 240)
                # Создаем темный цвет для границы
                border_color = QColor(40, 40, 40)
                # Создаем перо толщиной 5 пикселей
                pen = QPen(border_color, 5, Qt.PenStyle.SolidLine)
                self.graphics_scene.addRect(i * 200, j * 200, 190, 190, 
                                         pen=pen,
                                         brush=QBrush(fill_color))
    
    def toggle_grid_size(self, event):
        """Переключение размера сетки прямоугольников"""
        self._is_large_grid = not self._is_large_grid
        self._add_rectangles_to_scene()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Устанавливаем светлую тему для приложения
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())