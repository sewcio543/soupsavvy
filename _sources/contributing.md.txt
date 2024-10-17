# Contributing

Thank you for your interest in contributing to `soupsavvy`! We welcome contributions from the community to improve and expand the functionality of this project. To ensure a smooth contribution process, please follow these guidelines:

## How to Contribute

### Reporting Issues

If you encounter a bug or have a feature request, please follow these steps:

1. **Check the Existing Issues**: Before submitting a new issue, make sure to check the [existing issues](https://github.com/sewcio543/soupsavvy/issues) to see if it has already been reported.
2. **Create a New Issue**: If the issue is not listed, open a new issue in the [Issues](https://github.com/sewcio543/soupsavvy/issues) section of the repository.
   - Provide a clear and descriptive title.
   - Include a detailed description of the problem or feature request.
   - If applicable, provide steps to reproduce the issue and any relevant screenshots or error messages.

Here's the updated `Pull Requests` section incorporating pre-commit setup:

---

### Pull Requests

We encourage you to submit pull requests (PRs) for bug fixes, enhancements, or documentation improvements. To ensure a smooth review process, please adhere to the following guidelines:

1. **Fork the Repository**: Create a fork of the `soupsavvy` repository on GitHub.

2. **Clone Your Fork**: Clone your fork to your local machine.

   ```bash
   git clone https://github.com/yourusername/soupsavvy.git
   ```

3. **Setup Environment**: Set up your environment by installing all necessary development dependencies.

   ```bash
   make setup
   ```

4. **Install Pre-commit Hooks**: Install pre-commit hooks to ensure code quality and consistency. They will be used on every commit to check for formatting, linting, and other issues.

   ```bash
   pre-commit install
   ```

5. **Checkout Current Development Branch**: Find the current development branch that follows semantic versioning and check out to it. It can look like: `dev/0.3.2`.

   ```bash
   git checkout dev/0.3.2
   ```

6. **Create a Branch**: Create a new branch from the development branch for your changes.

   ```bash
   git checkout -b feature/your-feature-name
   ```

7. **Make Changes**: Implement your changes or improvements.

8. **Check your changes**: Follow guidelines described below to ensure that your changes fulfill the requirements.

9. **Commit Your Changes**: Commit your changes with a descriptive message.

   ```bash
   git add .
   git commit -m "Add a descriptive message about your changes"
   ```

10. **Push Your Branch**: Push your changes to your fork.

   ```bash
   git push origin feature/your-feature-name
   ```

11. **Create a Pull Request**: Open a pull request from your fork to the `soupsavvy` repository with the development branch as the base.

- Provide a clear description of your changes and the motivation behind them.
- Reference any relevant issues by mentioning them in your PR description.
- Add any relevant labels to your PR (e.g., bugfix, enhancement, documentation, demos, feature).

---

### Code Style

- Follow the existing code style and conventions used in the project. Use the `black` code formatter to ensure consistent formatting with version specified in `requirements-dev.txt`. To ensure the format is correct, run:

  ```bash
  make format
  ```

  or:

  ```bash
  python -m black . --diff --check
  ```

- Use `flake8` to check for linting issues. To run the linter, use:

  ```bash
  make lint
  ```

  or:

  ```bash
   python -m flake8 --config tox.ini
   ```

- Ensure that your code is well-formatted and follows Python’s PEP 8 guidelines.
- Use meaningful names for variables, functions, and classes.

### Testing

- Run the test suite to ensure that your changes do not break existing functionality. You can run the tests using:

  ```bash
  make test
  ```

  or:

  ```bash
  python -m pytest
  ```

- Write new tests for any new features or bug fixes. Test are located in `tests` directory, that should mirror the structure of the `soupsavvy` package.
- Make sure that all tests pass before submitting your pull request.
- Make sure every new line of code is covered by tests. Run `coverage` with:

  ```bash
  make coverage
  ```

  or:

  ```bash
   python -m coverage run -m pytest
   python -m coverage report
   python -m coverage html
  ```

- Ensure that package is installed correctly after new changes:

  ```bash
  make install
  ```

  or:

  ```bash
   python -m pip install -e .
   python -m pip show soupsavvy
  ```

- Check if type hints are defined correctly for your changes:

  ```bash
  make typecheck
  ```

  or:

  ```bash
   python -m mypy . || true
   python -m mypy --install-types --non-interactive
   python -m mypy . --ignore-missing-imports
  ```

### Documentation

- Update the documentation to reflect any changes or new features introduced.
- Ensure that your documentation is clear and provides helpful information for users and other contributors.
- Ensure the documentation builds properly after applying any changes to code or documentation setup:

    ```bash
    make docu
    ```

   or:

   ```bash
   bash docs/sphinx_run.sh
   git clean -fd docs/source/*.rst
   ```

### Demos

- Update any relevant demos to reflect any changes or new features introduced.
- Ensure that your demos include clear instructions and examples.
- Ensure that the demos execute without errors:

    ```bash
    make run_demos
    ```

   or:

   ```bash
   python -m pytest --nbmake -v demos/
   ```

### CI

- Ensure that all CI checks for your branch pass successfully.
- Wait for PR review and approval before merging your changes to development branch.
- Github Actions CI should cover all necessary checks described in this document, so every fault will be caught immediately.

## Contact

If you have any questions or need further assistance, feel free to reach out to the maintainers via GitHub issues.

Thank you for contributing to `soupsavvy`!
