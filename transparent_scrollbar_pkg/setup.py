from setuptools import setup, find_packages

setup(
    name="transparent_scrollbar",
    version="1.0.0",
    description="Оптимизированные прозрачные скроллбары для PyQt6",
    author="Ilya Shirokolobov",
    author_email="ilya.shirokolobov@gmail.com",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: User Interfaces",
    ],
    python_requires=">=3.6",
) 