"""Setup configuration for tennis prediction utilities."""

from pathlib import Path
from setuptools import setup

# Read the long description from README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="tennis-prediction",
    version="0.1.0",
    description="Simple tennis match win probability calculator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Oleksandr",
    url="https://github.com/Oleksandr94-us/hello-world",
    py_modules=["tennis_prediction"],
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tennis-prediction=tennis_prediction:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
