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
        self.resize(800, 600)
        
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
        vsb.bg_alpha = 10
        vsb.handle_alpha = 100
        vsb.hover_alpha = 150
        vsb.pressed_alpha = 200
        vsb.auto_hide = True
        vsb.use_dark_theme = True
        
        hsb = HorizontalScrollBar()
        hsb.bg_alpha = 10
        hsb.handle_alpha = 100
        hsb.hover_alpha = 150
        hsb.pressed_alpha = 200
        hsb.auto_hide = True
        hsb.use_dark_theme = True
        
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
            scroll_bar_width=10,
            auto_hide=False,
            use_dark_theme=False
        )
        
        # Добавляем кнопку для переключения темы
        theme_btn = QLabel("Нажмите здесь для переключения темы")
        theme_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        theme_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        theme_btn.setStyleSheet("background-color: #e0e0e0; padding: 10px; border-radius: 5px;")
        theme_btn.mousePressEvent = self.toggle_theme
        
        layout.addWidget(theme_btn)
        layout.addWidget(self.theme_scroll_area)
        
        return tab
    
    def toggle_theme(self, event):
        # Инвертируем текущую тему
        is_dark = self.theme_scroll_area.property("using_dark_theme")
        new_theme = not is_dark if is_dark is not None else True
        
        # Применяем новую тему
        toggle_scrollbar_theme(self.theme_scroll_area, new_theme)
        
        # Сохраняем информацию о текущей теме
        self.theme_scroll_area.setProperty("using_dark_theme", new_theme)
        
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
        
        # Добавляем элементы на сцену (цветные прямоугольники)
        for i in range(10):
            for j in range(10):
                color = QColor.fromHsv(((i * 10 + j) * 15) % 360, 200, 200)
                scene.addRect(i * 200, j * 200, 190, 190, 
                             pen=QPen(Qt.PenStyle.NoPen),
                             brush=QBrush(color))
        
        # Применяем прозрачные скроллбары к QGraphicsView
        vsb, hsb = apply_scrollbars_to_graphics_view(
            graphics_view,
            bg_alpha=10,
            handle_alpha=100,
            hover_alpha=150,
            pressed_alpha=200,
            scroll_bar_width=10,
            use_dark_theme=True,
            auto_hide=True
        )
        
        description = QLabel(
            "Демонстрация прозрачных скроллбаров для QGraphicsView.\n"
            "Скроллбары появляются при наведении на область просмотра и автоматически скрываются."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setFont(QFont("Arial", 11))
        
        layout.addWidget(description)
        layout.addWidget(graphics_view)
        
        return tab

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