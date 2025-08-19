
## Code Style Guide

- All code must follow [PEP8](https://www.python.org/dev/peps/pep-0008/) standards.
- Use `black` for automatic code formatting (Python 3.11).
- Use `flake8` for linting. Fix all errors and warnings before submitting code.
- Remove unused imports and variables with `autoflake`.
- Keep line lengths under 120 characters when possible, but prioritize readability for long URLs or error messages.
- Use meaningful variable and function names.
- Add docstrings to all public functions and classes.

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to enforce code style and linting before every commit.

**Setup:**
1. Install pre-commit: `pip install pre-commit`
2. Install hooks: `pre-commit install`

Hooks will automatically run on `git commit`. To run them manually:

    pre-commit run --all-files

**Do not commit code that fails pre-commit checks.**

## Submitting Code
- Ensure all tests pass before submitting a pull request.
- Follow the code style and documentation guidelines above.
- Update or add tests for new features or bug fixes.
- Update documentation as needed.

