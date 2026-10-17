# Changelog

Notable repository-level changes are documented in this file. The project follows a research-oriented development process; entries describe artifacts and milestones, not claims of validated performance.

## Unreleased

### Planned

- Implement the first constrained optimization baseline.
- Add stochastic scenario generation and comparative evaluation scripts.
- Define stable interfaces between forecasting and optimization modules.

## 2026-10-17

### Added

- A dedicated related-work index, review guidelines, and a paper note on congestion-aware route recommendation (Yi et al., 2024).
- A paper note on Temporal Fusion Transformers (Lim et al., 2021), including input availability and uncertainty considerations.
- Five versioned synthetic allocation scenarios covering scarce and surplus budgets, zero demand, zero budget, and a closed location.
- A standard-library scenario runner with Markdown and JSON reports for allocation totals, unmet demand, unused budget, and feasibility.
- Tests for known fixture outcomes, repeatability, invalid inputs, and both command-line output formats.
- A visible README results table and documented configuration schema and feasibility tolerance.

## 2026-10-11

### Added

- A mathematical framework for forecasting, constrained objectives, sequential pricing, congestion-aware recommendation, and grounded language interfaces.
- An explicit linear capacity-allocation model with unmet-demand and adjustment variables, linked to the current proportional heuristic.
- An evaluation protocol covering metric definitions, reference methods, temporal validation, ablations, and reproducible reporting.
- A README scientific-foundations section linking the new specifications.

### Clarified

- The assumptions under which proportional allocation already minimizes total unmet demand.
- The distinction between interval service capacity and concurrent occupancy, plus zero-demand metric handling and objective scaling.
- The implementation status of the specified methods; no new solver or experimental results are included.

## 2026-10-09

### Added

- A runnable proportional-allocation heuristic with JSON output and input validation, using only the Python standard library.
- Tests for scarce and surplus budgets, zero cases, invalid inputs, and feasibility across 100 seeded synthetic cases.
- A README quick start and documented assumptions for the heuristic comparator.

## 2026-10-07

### Added

- A public roadmap and workstream status table in the README.
- A technical specification for the next mathematical optimization milestone.
- Explicit validation criteria for feasibility, reproducibility, and baseline comparison.

### Clarified

- The distinction between established repository structure, current design work, and planned implementation.
- The interpretation of status labels to avoid implying unreported empirical results.

## 2026-08-27

### Added

- Initial research-oriented repository structure.
- Research vision, module descriptions, architecture, and reproducibility objectives.
