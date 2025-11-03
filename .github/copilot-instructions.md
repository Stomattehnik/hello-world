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
* **Language**: User-facing documentation (README.md) is primarily in Ukrainian (українська мова). Technical documentation (like this file), code comments, and docstrings may be in English for broader accessibility.
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

* The project is designed for educational and demonstration purposes
* Focus on transparency and explainability of predictions
* Mobile deployment is a key consideration for model design
# GitHub Copilot Instructions

## Project Overview

This repository contains a tennis prediction system with multiple components:
- Python scripts for tennis match outcome prediction
- Machine learning pipelines (Gradient Boosting + Neural Networks)
- Betting data parsing utilities
- Android mobile application (Kotlin/Jetpack Compose)

## Code Style and Conventions

### Python
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Document functions with clear docstrings
- Keep functions focused and modular
- Prefer descriptive variable names over short ones

### Android/Kotlin
- Follow Kotlin coding conventions
- Use Jetpack Compose for UI components
- Location: `android-app/` directory
- Target API level: 26+ (Android 8.0+)

## Testing Requirements

### Test Framework
- Use `pytest` for Python tests (version 8.0.0+)
- All tests are located in the `tests/` directory
- Test files follow naming convention: `test_*.py`

### Testing Guidelines
- Always write tests for new features
- Maintain or improve existing test coverage
- Run tests with: `pytest -v`
- Tests should be clear, focused, and independent
- Use descriptive test names that explain what is being tested

### Existing Test Files
- `tests/test_betting_data.py` - Tests for betting data parsing
- `tests/test_hybrid_pipeline.py` - Tests for ML pipeline
- `tests/test_tennis_prediction.py` - Tests for tennis prediction logic

## Security Best Practices

- Never commit secrets, API keys, or credentials
- Validate all user inputs
- Use secure random number generation for sensitive operations
- Follow OWASP guidelines for web/API security
- Keep dependencies up to date

## Technology Stack

### Python
- Core language for ML and data processing
- Key dependencies are in `requirements.txt`
- Uses NumPy, pandas (implied from code structure)
- Machine learning: scikit-learn patterns

### Android
- Kotlin with Jetpack Compose
- Android Studio Giraffe+ recommended
- JDK 17
- SDK 34

## Dependencies

### Installation
```bash
pip install -r requirements.txt
```

Or for development mode:
```bash
pip install -e .
```

### Adding New Dependencies
- Add to `requirements.txt` for Python packages
- Update Android `build.gradle` files for Android dependencies
- Always specify version constraints
- Check for security vulnerabilities before adding

## Key Files and Modules

- `tennis_prediction.py` - Main tennis prediction script with CLI
- `hybrid_pipeline.py` - Hybrid ML model (Gradient Boosting + Neural Network)
- `betting_data.py` - Betting feed parser and training data builder
- `numpy.py` - NumPy-related utilities
- `setup.py` - Package setup configuration
- `android-app/` - Native Android application

## Documentation

- README.md contains user-facing documentation in Ukrainian
- Keep documentation updated when adding features
- Include usage examples for new functionality
- Document any breaking changes clearly

## Common Tasks

### Running Tests
```bash
pytest -v
```

### Running Tennis Predictions
```bash
python tennis_prediction.py --player_one-name "Player 1" --player_one-ranking 1 \
  --player_one-serve 0.62 --player_one-return 0.46 \
  --player_one-surface 0.80 --player_one-form 0.90 \
  --player_two-name "Player 2" --player_two-ranking 4 \
  --player_two-serve 0.58 --player_two-return 0.41 \
  --player_two-surface 0.74 --player_two-form 0.85
```

### Batch Processing
```bash
python tennis_prediction.py --matches-file matches.csv --output predictions.csv
```

## Best Practices for Contributors

1. **Make minimal changes** - Only modify what's necessary to fix the issue
2. **Test thoroughly** - Run all tests before submitting changes
3. **Follow existing patterns** - Match the style and structure of existing code
4. **Update documentation** - Keep README and docstrings current
5. **Use descriptive commit messages** - Explain what and why, not just what
6. **Preserve working code** - Don't modify unrelated functionality

## Language Note

The README and some documentation are in Ukrainian (українська). When updating user-facing documentation, maintain the same language for consistency.
