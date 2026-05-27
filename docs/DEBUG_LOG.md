# Debug Log

## 2026-05-27

### Bug: silent parse failure when model uses label aliases
- **Symptom:** `POST /api/analyze` returned HTTP 200 with `"summary": "Summary unavailable from model response."` and no error field — frontend showed broken output with no visible alert.
- **Root cause:** `parse_structured_response()` only matched the exact string `"summary:"`. When the model responded with `"Overview:"`, `"Impression:"`, or `"Assessment:"` instead, the summary field was silently left empty.
- **Fix:** Introduced `_LABEL_ALIASES` — a canonical-key → accepted-prefixes map. Parser now matches any known alias for each section label. Added `parse_warning: bool` field to `AnalyzeResponse` so the frontend can surface a visible warning when parsing partially fails.
- **Additional:** Expanded `KNOWN_FINDINGS` from 8 → 20 terms to improve fallback coverage. Updated `build_prompt()` to instruct the model to use labels exactly. Updated `docs/API.md` to document `parse_warning` and `source` values. Frontend now shows a yellow warning banner when `parse_warning` is true or `source === "fallback"`. Added Clear button and character counter to the input panel.

## 2025-02-14
- Command: `git status -sb`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; continued with commands in the sandbox and noted the warning.

## 2025-02-14
- Command: `mkdir -p PROMPTS scripts docs fine-tuning backend frontend demo`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `touch PROMPTS/.gitkeep scripts/.gitkeep docs/.gitkeep fine-tuning/.gitkeep backend/.gitkeep frontend/.gitkeep demo/.gitkeep`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `ls -l README.md && cat README.md`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; continued with commands in the sandbox and noted the warning.

## 2025-02-14
- Command: `cat <<'EOF' > README.md ... EOF`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `cat <<'EOF' > backend/.env.example ... EOF`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `cat <<'EOF' > frontend/.env.example ... EOF`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `cat <<'EOF' > docs/TRAINING.md ... EOF`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `ls -R`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `python3 fine-tuning/prepare_data.py --total 8000 --eval-ratio 0.1`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `python3 fine-tuning/validate_data.py`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `python3 fine-tuning/evaluate_model.py --eval-path fine-tuning/data/eval_data.jsonl`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `ls -la fine-tuning/data/processed`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `rg -n "generated_text|call_hf_inference|analyze_report" backend/main.py`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `cp .env.example .env`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; command still completed.

## 2025-02-14
- Command: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- Error: `zsh:1: command not found: uvicorn`
- Diagnosis: `uvicorn` is not installed in the current environment.
- Fix: Install backend dependencies (e.g., `pip install -r backend/requirements.txt`) and retry.

## 2025-02-14
- Command: `pip install -r backend/requirements.txt`
- Error: `zsh:1: command not found: pip`
- Diagnosis: Python/pip is not available on PATH in this shell.
- Fix: Use `python3 -m pip install -r backend/requirements.txt` or set up a venv.

## 2025-02-14
- Command: `python3 -m pip install -r backend/requirements.txt`
- Error: `error: externally-managed-environment`
- Diagnosis: System Python is managed by Homebrew (PEP 668) and blocks global installs.
- Fix: Create and use a virtual environment (`python3 -m venv .venv && source .venv/bin/activate`) before installing.

## 2025-02-14
- Command: `python3 -m venv .venv && source .venv/bin/activate && python3 -m pip install -r backend/requirements.txt`
- Error: `ERROR: No matching distribution found for fastapi`
- Diagnosis: Network access is restricted, so pip cannot reach PyPI to download dependencies.
- Fix: Re-run pip install with network access approval or install via an allowed networked environment.

## 2025-02-14
- Command: `/Users/momossss/Documents/GitHub/MedExplain_AI/.venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- Error: `ERROR:    [Errno 1] Operation not permitted`
- Diagnosis: The auto-reloader attempted a system call blocked by the sandbox.
- Fix: Run uvicorn without `--reload` in this environment.

## 2025-02-14
- Command: `/Users/momossss/Documents/GitHub/MedExplain_AI/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000`
- Error: `error while attempting to bind on address ('0.0.0.0', 8000): operation not permitted`
- Diagnosis: The sandbox blocks binding to 0.0.0.0.
- Fix: Bind to `127.0.0.1` instead.

## 2025-02-14
- Command: `/Users/momossss/Documents/GitHub/MedExplain_AI/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000`
- Error: `error while attempting to bind on address ('127.0.0.1', 8000): operation not permitted`
- Diagnosis: The sandbox blocks binding to local ports.
- Fix: Run uvicorn from a local terminal outside the sandbox.

## 2025-02-14
- Command: `git checkout -b phase-setup-debug-log`
- Error: `fatal: cannot lock ref 'refs/heads/phase-setup-debug-log': Unable to create '/Users/momossss/Documents/GitHub/MedExplain_AI/.git/refs/heads/phase-setup-debug-log.lock': Operation not permitted`
- Diagnosis: Sandbox permissions prevented writing to `.git/refs` for branch creation.
- Fix: Retry with escalated permissions for git branch creation.

## 2025-02-14
- Command: `git add -A`
- Error: `fatal: Unable to create '/Users/momossss/Documents/GitHub/MedExplain_AI/.git/index.lock': Operation not permitted`
- Diagnosis: Sandbox permissions prevented writing to the git index.
- Fix: Retry with escalated permissions for git add/commit steps.

## 2025-02-14
- Command: `git status -sb`
- Error: `/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted`
- Diagnosis: Homebrew shellenv attempts to invoke `/bin/ps`, which is blocked by the current sandbox.
- Fix: No local fix applied; continued with commands in the sandbox and noted the warning.
