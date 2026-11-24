# AI Project Template

A modern Python boilerplate for building AI and GenAI applications.

## Project Structure

```text
├── app/              # Main application code
├── docker/           # Docker configurations
├── docs/             # Documentation files
├── playground/       # Experimental code and notebooks
├── .env.example      # Environment variables template
├── pyproject.toml    # Project dependencies and metadata
└── uv.lock           # Locked dependencies
```

## Setup

1. Install dependencies:
   ```
   uv sync --dev
   ```

2. Add your API keys to `.env`.

## Usage

Run the app:
```
uv run python app/main.py
```

For experimentation, open any notebook in `playground/` and select the project's `.venv` as the kernel.

## Notes

- Never commit `.env` — it's gitignored.
- Use `uv add <package>` to add dependencies (updates `pyproject.toml` and `uv.lock` automatically).
- Use `uv add --dev <package>` for development-only tools.
