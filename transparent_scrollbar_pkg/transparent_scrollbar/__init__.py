#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Библиотека прозрачных, анимированных и настраиваемых скроллбаров для PyQt6.

Предоставляет классы и функции для замены стандартных скроллбаров на прозрачные,
с поддержкой анимации, различных тем и эффектов при наведении мыши.
"""

from .transparent_scroller import (
    BaseScrollBar,
    VerticalScrollBar,
    HorizontalScrollBar,
    OverlayScrollArea,
    ScrollBarThemeManager,
    ScrollBarAnimationManager,
    apply_overlay_scrollbars,
    toggle_scrollbar_theme
)

from .graphics_view_scroller import (
    GraphicsViewScrollBar,
    GraphicsViewVerticalScrollBar,
    GraphicsViewHorizontalScrollBar,
    GraphicsViewScrollManager,
    GraphicsViewScrollBarThemeManager,
    apply_scrollbars_to_graphics_view,
    toggle_graphics_view_scrollbar_theme
)

__all__ = [
    # Классы и функции из transparent_scroller
    'BaseScrollBar',
    'VerticalScrollBar',
    'HorizontalScrollBar',
    'OverlayScrollArea',
    'ScrollBarThemeManager',
    'ScrollBarAnimationManager',
    'apply_overlay_scrollbars',
    'toggle_scrollbar_theme',
    
    # Классы и функции из graphics_view_scroller
    'GraphicsViewScrollBar',
    'GraphicsViewVerticalScrollBar',
    'GraphicsViewHorizontalScrollBar',
    'GraphicsViewScrollManager',
    'GraphicsViewScrollBarThemeManager',
    'apply_scrollbars_to_graphics_view',
    'toggle_graphics_view_scrollbar_theme'
]

__version__ = '0.5.0' 