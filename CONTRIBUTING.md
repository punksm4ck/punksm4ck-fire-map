# Contributing to Aegis Omni-Tracker

Thanks for your interest in contributing. This is a focused utility project — contributions that improve reliability, portability, or extend the data pipeline are most welcome.

---

## Ways to Contribute

- **Bug reports** — open an Issue with steps to reproduce, OS, and Python version
- **New incident seeds** — PRs adding verified incidents to `default_markers` (include source link in PR description)
- **Feed improvements** — alternate RSS sources, better geocoding fallbacks, or rate-limit handling
- **UI enhancements** — marker clustering, color-coding by incident type, export features
- **Cross-platform fixes** — especially Windows font/DPI and macOS Tkinter quirks

---

## Ground Rules

1. Keep the single-file architecture. `aegis_fire_map.py` is intentionally self-contained.
2. No new required dependencies without strong justification — the install footprint should stay minimal.
3. All new location data must come from verifiable public sources (news articles, official fire dept reports, etc.).
4. Don't commit `aegis_omni_db.json` — it's in `.gitignore` for a reason (contains dynamically scraped data).
5. Don't commit `.bak_*` patch backup files.

---

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/aegis-omni-tracker.git
cd aegis-omni-tracker
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python aegis_fire_map.py
```

---

## Pull Request Process

1. Fork the repo and create a branch: `git checkout -b fix/your-description`
2. Make your changes
3. Verify the app launches cleanly: `python aegis_fire_map.py`
4. Run a quick syntax check: `python -m py_compile aegis_fire_map.py`
5. Open a PR with a clear description of what changed and why
