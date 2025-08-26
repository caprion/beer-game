## Delivery Plan and Tasks

### Milestone 1 — Scaffolding and Docs
- Create PRD and Architecture docs [done].
- Set up Python package skeleton and requirements.
- Add initial notebooks.

### Milestone 2 — Engine and Interfaces
- Implement `interfaces.State` and `AgentProtocol`.
- Implement minimal `SimulationRunner` supporting four roles, delays, and logging.
- Add basic constant demand process and default parameters.

### Milestone 3 — Behavioral Profiles (MVP)
- Implement five rule-based profiles (Aggressive, Myopic, Conservative, Signal Chaser, Passive) and a Random baseline.
- Parameterize profiles via constructor args.
- Add unit tests for decision rules.

### Milestone 4 — Metrics and Plots
- Compute bullwhip, service level, inventory/backlog summaries, costs.
- Plot time series and bullwhip bar charts.

### Milestone 5 — Human-in-the-Loop Option
- Implement `HumanAgent` that uses callback or `input()` to return order.
- Guard with non-interactive fallback for batch runs.

### Milestone 6 — Experimentation and Validation
- Notebook to run profile mixtures and compare.
- Parameter sweeps and random seed control.

### Acceptance Criteria
- See PRD AC1–AC4.

### Risks
- DOCX behavioral details need confirmation for exact formulas.
- Time synchronization of lead times must be correct to avoid artifacts.


