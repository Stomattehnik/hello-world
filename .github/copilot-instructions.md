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
