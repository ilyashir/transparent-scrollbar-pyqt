from setuptools import setup

setup(
    name="transparent_scrollbar",
    version="0.1.1",
    description="Transparent scrollbars for PyQt6",
    author="Ilya Shirokolobov",
    author_email="ilya.shirokolobov@gmail.com",
    py_modules=["transparent_scrollbar.transparent_scroller", "transparent_scrollbar.graphics_view_scroller"],
    packages=["transparent_scrollbar"],
    install_requires=[
        "PyQt6>=6.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 