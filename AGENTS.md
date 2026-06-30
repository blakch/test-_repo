# AGENTS.md

## Cursor Cloud specific instructions

This repo contains two independent Streamlit apps managed with `uv` (each has its own `pyproject.toml` + `uv.lock` + `.venv`):

| App | Path | Python | Purpose |
| --- | --- | --- | --- |
| `younginhr` | `younginhr/` | 3.10+ (uses 3.12) | 전력기술인 경력확인서 PDF → 종합 경력확인서 Excel 변환 (GPT-4o Vision OCR) |
| `younginmatch` | `younginmatch/` | 3.13 (uv-managed) | RFP 평가기준 기반 AI 인력 매칭 (GPT-4o) |

### Running (dev mode)
- Run each app from its own directory, e.g. `uv run streamlit run app.py --server.port 8501` (use a distinct port per app, e.g. 8501 / 8502).
- `uv` installs to `~/.local/bin` (already added to `~/.bashrc`).

### Non-obvious caveats
- **OpenAI key required for AI features.** Both apps call `gpt-4o` and need `OPENAI_API_KEY`. `younginhr` hard-stops at startup with an error page if the key is missing/placeholder (see `app.py` precheck). `younginmatch` still loads and renders (CV/실적 data load from local Excel), and also accepts a key pasted into its sidebar for the current browser session; the matching/chat actions need a valid key.
- **Key sources.** `younginhr` reads `younginhr/.env` then repo-root `.env`; `younginmatch` reads repo-root `.env` then `younginmatch/.env`. `.env` files are gitignored.
- **Local data files** (`younginmatch/CV.xlsx`, `영인에너지솔루션_실적정리.xlsx`, `younginhr/sample/*`) are required for the apps to work and are committed in the repo.
- No test suite, linter config, or pre-commit hooks exist. "Build/lint" check = `uv run python -m py_compile app.py *.py` per app.
