# Contributing to Caelestia

Thank you for your interest in contributing to Caelestia! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone. We expect all contributors to:

- Be respectful and considerate in communication
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/caelestia.git
   cd caelestia
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/caelestia-dots/caelestia.git
   ```

## Development Setup

### Prerequisites

- Arch Linux (or Arch-based distribution)
- Python 3.13+
- CMake, Ninja, Clang
- Fish shell
- Hyprland

### Testing Your Changes

1. **For the installer:**
   ```bash
   bash caelestia-install.sh --noconfirm --skip-packages
   ```

2. **For the CLI:**
   ```bash
   cd cli-1.0.6
   pip install --editable .
   caelestia --help
   ```

3. **For the shell:**
   ```bash
   cd shell-1.5.1
   cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug
   cmake --build build
   ```

### Rebuilding After Changes

```bash
bash caelestia-install.sh --rebuild
```

## Making Changes

### Branching Strategy

1. Create a new branch from `main`:
   ```bash
   git checkout main
   git pull upstream main
   git checkout -b feature/my-feature
   ```

2. Make your changes following the guidelines below

### Code Style

#### Shell Scripts (Bash)
- Use `shellcheck` for linting
- Follow Google Shell Style Guide
- Use 2 spaces for indentation
- Always use `set -eo pipefail`

#### Python (CLI)
- Follow PEP 8
- Use type hints where possible
- Maximum line length: 120 characters

#### C++/QML (Shell)
- Follow the project's existing style
- Use ClangFormat for formatting
- Enable all compiler warnings

### Commit Messages

Use clear, descriptive commit messages:

```
feat(installer): add --modules option for selective install
fix(cli): resolve clipboard history crash on empty selection
docs(readme): update installation instructions
```

Format: `type(scope): description`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Submitting Changes

1. Ensure all tests pass locally
2. Push your branch:
   ```bash
   git push origin feature/my-feature
   ```
3. Open a Pull Request against `main`
4. Fill out the PR template completely
5. Wait for review and address any feedback

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-reviewed code changes
- [ ] Tests added/updated (if applicable)
- [ ] Documentation updated (if applicable)
- [ ] No merge conflicts

## Reporting Bugs

Before submitting a bug report:

1. Check if the bug has already been reported
2. Update to the latest version
3. Collect relevant information:
   - Caelestia version
   - OS and Hyprland version
   - Steps to reproduce
   - Expected vs actual behavior
   - Log files (`/tmp/caelestia-install.log`)

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.yml) for submissions.

## Suggesting Features

We welcome feature suggestions! Before submitting:

1. Check if the feature already exists
2. Consider if it aligns with the project's goals
3. Think about implementation complexity

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.yml) for submissions.

## Questions?

- Join our [Discord](https://discord.gg/BGDCFCmMBk)
- Open a Discussion on GitHub
- Check the [Wiki](https://github.com/caelestia-dots/caelestia/wiki)

---

Thank you for contributing to Caelestia! 💫
