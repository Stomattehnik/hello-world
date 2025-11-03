# GitHub Copilot Instructions for hello-world Repository

## Project Overview

This repository contains a tennis match prediction system with multiple components:

* **Python scripts** for tennis match win probability calculations
* **Machine learning pipeline** with gradient boosting and neural networks
* **Betting data parser** for processing bookmaker feeds
* **Android application** (Kotlin/Jetpack Compose) with native UI
* **Test suite** using pytest for Python components

The project focuses on providing transparent, intuitive probability forecasts for tennis matches using statistical analysis and machine learning.

## Repository Structure

* `tennis_prediction.py` - CLI tool for single match and batch predictions
* `hybrid_pipeline.py` - ML pipeline combining gradient boosting and neural networks
* `betting_data.py` - Parser for bookmaker feed data
* `numpy.py` - Utility functions
* `android-app/` - Native Android application
* `tests/` - Python test suite using pytest
* `requirements.txt` - Python testing dependencies
* `setup.py` - Package configuration

## Coding Standards

### Python Code

* **Python Version**: Target Python 3.9+ (support up to 3.12)
* **Style**: Follow PEP 8 conventions
* **Type Hints**: Use type hints for function signatures (from `__future__ import annotations`)
* **Docstrings**: Use triple-quoted docstrings for modules, classes, and functions
* **Imports**: Group imports logically (standard library, third-party, local)
* **Dataclasses**: Use `@dataclass(slots=True)` for data structures
* **Error Handling**: Raise descriptive exceptions with proper error messages
* **Constants**: Use UPPER_CASE for constants
* **Functions**: Use snake_case for function and variable names
* **Private Functions**: Prefix with underscore (e.g., `_positive_float`)

### Android/Kotlin Code

* **Language**: Kotlin for Android development
* **UI Framework**: Jetpack Compose
* **Target SDK**: Android SDK 34
* **Min SDK**: API 26 (Android 8.0+)
* **Build Tool**: Gradle with Kotlin DSL
* **Naming**: Use TitleCase for Kotlin classes and files
* **Code Location**: `android-app/app/src/main/java/com/example/tennispredictor/`

## Testing Requirements

* **Framework**: pytest (version 8.0.0 or higher)
* **Coverage**: Write unit tests for all new functionality
* **Test Location**: Place tests in `tests/` directory
* **Test Naming**: Prefix test files with `test_` (e.g., `test_tennis_prediction.py`)
* **Test Functions**: Use descriptive test names starting with `test_`
* **Assertions**: Use pytest assertions and `pytest.approx()` for floating-point comparisons
* **Test Data**: Use helper functions (e.g., `make_player()`) for creating test fixtures
* **Run Tests**: Execute with `pytest` command from project root

### Example Test Pattern

```python
def test_descriptive_name() -> None:
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_value
```

## Libraries and Dependencies

### Approved Python Libraries

* **Testing**: pytest (>=8.0.0)
* **Type Checking**: mypy (>=1.0.0) - development only
* **Standard Library**: Prefer standard library over third-party when possible

### Avoid

* Do not add unnecessary dependencies
* Avoid deprecated APIs
* Do not introduce jQuery or other legacy libraries

## Security Guidelines

* **Secrets**: Never commit API keys, passwords, or tokens to the repository
* **Input Validation**: Validate all user inputs, especially from CLI arguments
* **Type Safety**: Use type hints and type checking to catch errors early
* **Error Messages**: Avoid exposing sensitive information in error messages
* **External Data**: Validate and sanitize all external data inputs (CSV files, betting feeds)

## Build and Test Commands

### Python Development

```bash
# Install in development mode
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov

# Type checking
mypy *.py

# Run the CLI tool
python tennis_prediction.py --help
```

### Android Development

* Open the `android-app/` directory in Android Studio
* Build: Use Android Studio build tools
* Requires: Android Studio Giraffe or newer, JDK 17
* Target: Android 8.0+ (API 26+)

## Files and Folders to Ignore

When making changes, ignore the following:

* `__pycache__/` - Python bytecode cache
* `*.pyc` - Compiled Python files
* `.pytest_cache/` - Pytest cache
* `*.egg-info/` - Python package metadata
* `dist/` - Distribution artifacts
* `build/` - Build artifacts
* `.mypy_cache/` - MyPy cache
* `android-app/build/` - Android build outputs
* `android-app/.gradle/` - Gradle cache
* `android-app/local.properties` - Local Android SDK configuration
* `.DS_Store` - macOS system files
* `.vscode/` - Editor-specific settings
* `.idea/` - IDE-specific settings

## Documentation Standards

* **README**: Keep README.md up to date with examples and usage instructions
* **Code Comments**: Add comments for complex logic or non-obvious decisions
* **Docstrings**: Document all public functions, classes, and modules
* **Language**: Documentation is in Ukrainian (українська мова)
* **Examples**: Include practical examples in docstrings and README

## Specific Guidelines

### Tennis Prediction Logic

* Maintain the existing formula and quality score calculation
* Rankings are 1-based (lower number = better rank)
* Statistics should be in range [0, 1] (e.g., serve percentage as decimal)
* Probability outputs must sum to 1.0

### Machine Learning Pipeline

* Use out-of-fold predictions for stacking
* Support serialization to JSON for model export
* Target ONNX/Core ML compatibility for mobile deployment
* Include evaluation metrics: ROC AUC, LogLoss, Brier Score, Accuracy

### CSV Processing

* Support both single match and batch modes
* Validate CSV structure and column names
* Handle missing or invalid data gracefully
* Output format should match input format

## Git Workflow

* Make minimal, focused changes
* Write clear, descriptive commit messages
* Test changes before committing
* Keep commits atomic and logical
* Do not commit build artifacts or temporary files

## Additional Notes

* This is a Ukrainian language project - documentation may be in Ukrainian
* The project is designed for educational and demonstration purposes
* Focus on transparency and explainability of predictions
* Mobile deployment is a key consideration for model design
