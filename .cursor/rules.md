## Cursor Project Instructions — Beer Game Behavioral Profiles

### Goals
- Implement pluggable behavioral agents and a small simulation engine.
- Use notebooks for experiments and plots.

### Conventions
- Python >= 3.10.
- Package under `profiles-beergame/src/profiles_beergame`.
- Use type hints and dataclasses.
- Avoid external heavy frameworks initially.

### How to Run
1) Create venv and install requirements:
   - `python -m venv .venv && .\.venv\Scripts\activate`
   - `pip install -r profiles-beergame/requirements.txt`
2) Launch Jupyter:
   - `jupyter lab` or `jupyter notebook`
3) Open `notebooks/00_quickstart.ipynb`.

### Editing Rules
- Keep agents in `profiles_beergame/agents/` and implement `decide_order(state) -> int`.
- Do not introduce global singletons; pass configuration explicitly.
- Keep plotting code in `profiles_beergame/plots/`.

### PR/Commit Guidance
- Small, focused edits with clear titles.
- Update docs when adding profiles or changing interfaces.


