# setup.py (в корне проекта)
from setuptools import setup, find_packages

setup(
    name="tiny-aria",
    version="0.1.0",
    description="Minimal ARIA Implementation - Adaptive Recursive Intelligence Assistant",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "networkx>=2.8",
        "nltk>=3.7",
        "spacy>=3.4",
        "pytest>=7.0",
        "pytest-cov>=4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=0.991",
        ]
    },
    entry_points={
        "console_scripts": [
            "tiny-aria=src.main:main",
            "tiny-aria-demo=src.demo_runner:main",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)