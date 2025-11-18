# Repository Guidelines

This document describes how to work safely and consistently in this repository. It applies to all files under this directory.

## Project Structure & Module Organization

- Root scripts: `dashboard.py` (Streamlit app), `Y_idx_newV2_spot.py` (data generation), `config.py` (UI and data config), `start_dashboard.sh` (one‑click start).
- Core modules: `components/` contains `data_loader.py`, `charts.py`, and `metrics.py` used by the dashboard.
- Data utilities: `yquant/` holds shared logic (`common/`, `config/`, `db/`).
- Styles & assets: `styles/custom.css` defines UI overrides; keep new assets small and organized by feature.
- Ad‑hoc tests and tooling live at the repo root (for example `test_load_data.py`).

## Build, Test, and Development Commands

- Install dependencies: `pip install -r requirements_dashboard.txt`
- Run dashboard (recommended): `./start_dashboard.sh`
- Run dashboard (manual): `streamlit run dashboard.py`
- Refresh source data: `python Y_idx_newV2_spot.py`
- Run data loading check: `python test_load_data.py`

Use a virtual environment (for example `python -m venv .venv && source .venv/bin/activate`) to isolate dependencies.

## Coding Style & Naming Conventions

- Language: Python 3.8+ with 4‑space indentation and PEP 8‑style layout.
- Names: `snake_case` for functions, variables, and modules; `PascalCase` for classes; `UPPER_SNAKE_CASE` for constants.
- Structure: keep UI logic in `dashboard.py` and reusable logic in `components/` or `yquant/`.
- Docstrings: add short, descriptive docstrings for public functions and modules.
- No formatter is enforced; match the style of nearby code and keep imports grouped (standard lib, third‑party, local).

## Testing Guidelines

- Prefer small, focused tests that exercise data loading and transformations.
- Keep new tests close to the code they cover (for example `test_*.py` at the root or in a future `tests/` folder).
- For simple checks, use `python test_your_module.py`; if you introduce `pytest`, follow its naming conventions and add a short usage note here.

## Commit & Pull Request Guidelines

- Commits: use clear, imperative messages in English, for example `feat: add Y index comparison chart` or `fix: handle empty market data`.
- Scope: keep commits focused on one logical change (feature, fix, or refactor).
- Pull requests: include a concise summary, motivation, and testing steps; attach screenshots for UI changes to `dashboard.py` or `styles/custom.css`.
- Avoid committing secrets or machine‑specific absolute paths; prefer configuration via `config.py` or environment variables.

## Communication Preference

- 与仓库维护者沟通时，请优先使用中文说明问题和改动背景；如需英文，请保持简洁并附必要的技术细节。
