# Contributing to GDrive Manager

Thank you for your interest in contributing to GDrive Manager! We welcome bug reports, feature suggestions, documentation enhancements, and code contributions.

---

## 1. Code of Conduct

All contributors are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat all community members with respect and professionalism.

---

## 2. Getting Started

1. **Fork and clone the repository**:
   ```powershell
   git clone https://github.com/mohitbhatt-du/gdrive-manager.git
   cd gdrive-manager
   ```

2. **Set up the Python development environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements-dev.txt
   python scripts/check_environment.py
   pre-commit install
   ```

---

## 3. Development Workflow & Git Standards

- **Branch Naming**: Use descriptive branch names:
  - `feat/feature-name`
  - `fix/bug-description`
  - `docs/doc-update`
  - `refactor/component-name`

- **Conventional Commit Messages**:
  Format commit messages according to Conventional Commits:
  - `feat: add bandwidth throttling setting`
  - `fix: resolve drive letter conflict during reconnect`
  - `docs: update installation guide for WinFsp 2.0`
  - `test: add integration test for bisync conflict`
  - `chore: update development dependencies`

---

## 4. Code Quality & Testing Requirements

Before submitting a Pull Request, ensure:
1. **Tests Pass**: Run `pytest -v tests/` (all 50+ tests must pass).
2. **Linting & Formatting**: Run `ruff check .` and `ruff format --check .`.
3. **No Regressions**: Do not remove existing tests without clear justification.
4. **Documentation**: Update corresponding markdown files in `docs/` if modifying features or configuration.

---

## 5. Submitting a Pull Request

1. Push your branch to your fork.
2. Open a Pull Request against the `main` branch.
3. Fill out the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md).
4. CI checks on Windows runners will automatically execute. Ensure all status checks pass.
