# Intelligent Tourism Control

A research-oriented framework for intelligent control in sustainable tourism management using reinforcement learning, mathematical optimization, predictive modeling, recommendation systems, retrieval-augmented generation, generative AI, autonomous sensing, and intelligent robotics.

## Try the Capacity Allocation Baseline

A first executable heuristic distributes a shared budget in proportion to demand capped by local capacity. Run this synthetic example from the repository root with Python 3.10 or later; no additional packages are required:

```sh
python src/tourism_control/optimization/proportional.py --demand 80 40 30 --capacity 60 50 30 --budget 90
```

The JSON output reports allocations (approximately `41.54`, `27.69`, and `20.77`), unmet demand, and unused budget. These are divisible capacity units for one time period. See the [model assumptions and next milestone](docs/research/optimization-milestone.md).

Run the baseline checks with:

```sh
python -m unittest discover -s tests/unit -v
```

## Reproduce the Scenario Checks

The baseline now includes five fixed synthetic scenarios covering scarce resources, surplus resources, zero demand, zero budget, and a closed location. Run the suite with Python 3.10 or later and no additional packages:

```sh
python scripts/evaluation/run_allocation_scenarios.py
```

| Scenario | Served | Unmet demand | Unused budget | Feasible |
|---|---:|---:|---:|:---:|
| scarce_budget | 90.00 | 60.00 | 0.00 | yes |
| surplus_budget | 50.00 | 50.00 | 50.00 | yes |
| zero_demand | 0.00 | 0.00 | 10.00 | yes |
| zero_budget | 0.00 | 30.00 | 0.00 | yes |
| closed_location | 20.00 | 30.00 | 20.00 | yes |

These are reproducible fixture results in divisible service-capacity units, not comparative performance evidence. For per-location allocations, unmet demand, and constraint residuals, append `--format json`. The [scenario configuration](configs/optimization/allocation-scenarios.json) and [evaluation protocol](docs/experiments/evaluation-protocol.md#available-scenario-runner) explain the inputs and feasibility tolerance.

## Scientific Foundations

The research specifications now define the equations, assumptions, and evaluation criteria for the planned decision-making modules:

- [Mathematical framework](docs/methodology/mathematical-framework.md): demand forecasting, uncertainty, constrained objectives, pricing policies, congestion-aware recommendation, and grounded language interfaces.
- [Optimization milestone](docs/research/optimization-milestone.md#deterministic-allocation-formulation): an explicit linear allocation model and its relationship to the implemented proportional heuristic.
- [Evaluation protocol](docs/experiments/evaluation-protocol.md): reference methods, metric definitions, temporal validation, ablations, and reproducibility requirements.

These documents describe planned methods. The proportional-allocation heuristic remains the current executable baseline.

## Research Vision

This project treats tourism management as a large-scale intelligent control problem.

The tourism ecosystem is modeled as a dynamic environment in which:

* sensing systems observe visitor flows and destination conditions,
* forecasting models estimate future system states,
* optimization algorithms determine management actions,
* reinforcement learning adapts policies through interaction,
* recommendation systems influence visitor behavior,
* large language models provide multilingual and explainable interaction,
* intelligent robotic systems can provide embodied assistance to visitors.

The long-term objective is to develop a closed-loop intelligent control architecture capable of continuously observing, predicting, optimizing, acting, and learning under dynamic and uncertain tourism conditions.

## Core Research Areas

### 1. UAV-Assisted Tourism Monitoring

Research on autonomous and adaptive sensing for tourism environments, including:

* UAV-assisted monitoring,
* fixed and mobile sensor integration,
* tourist-density estimation,
* computer vision,
* edge computing,
* multi-UAV coordination,
* adaptive sensing,
* coverage optimization,
* resource allocation.

### 2. Predictive Modeling of Tourist Flows

Development of predictive models for tourism demand and mobility, including:

* tourism-demand forecasting,
* spatio-temporal visitor-flow prediction,
* airport arrival forecasting,
* port and cruise arrival forecasting,
* deep learning,
* probabilistic forecasting,
* Bayesian forecasting,
* uncertainty quantification.

### 3. Reinforcement Learning for Dynamic Pricing

Development of adaptive pricing mechanisms for tourism systems, including:

* price elasticity modeling,
* capacity-constrained decision making,
* Markov Decision Process formulation,
* reinforcement learning,
* multi-objective optimization,
* congestion mitigation,
* visitor-flow redistribution,
* sustainability-aware pricing.

### 4. Intelligent Recommendation Systems

Development of recommendation mechanisms that balance personalization and destination-level objectives, including:

* visitor-profile modeling,
* context-aware recommendation,
* preference learning,
* reinforcement learning-based recommendation,
* multi-objective recommendation,
* overcrowding-aware recommendation,
* adaptive feedback mechanisms.

### 5. Large Language Models and Generative AI

Development of domain-oriented language intelligence for tourism applications, including:

* open-source large language models,
* domain adaptation,
* multilingual interaction,
* generative AI,
* explainable recommendations,
* personalized tourism assistance,
* cultural storytelling.

### 6. Retrieval-Augmented Generation

Development of grounded and knowledge-aware language services, including:

* regional knowledge bases,
* tourism corpus construction,
* semantic retrieval,
* vector databases,
* geographic retrieval,
* Retrieval-Augmented Generation,
* response grounding,
* RAG evaluation.

### 7. Mathematical Optimization

Optimization methods support multiple components of the intelligent control framework, including:

* constrained optimization,
* multi-objective optimization,
* resource allocation,
* capacity management,
* route and coverage optimization,
* congestion reduction,
* decision making under uncertainty.

### 8. Intelligent Robotics

Investigation of embodied AI systems for tourism environments, including:

* intelligent robotic tour assistants,
* multilingual human-robot interaction,
* LLM-enabled conversational robots,
* reinforcement learning for adaptive interaction,
* navigation and visitor guidance,
* context-aware robotic recommendation,
* personalized cultural storytelling.

## Intelligent Control Architecture

The project follows a closed-loop architecture:

```text
UAVs + Fixed Sensors
        |
        v
Monitoring and State Estimation
        |
        v
Predictive Analytics and Forecasting
        |
        v
Reinforcement Learning + Optimization
        |
        v
Dynamic Pricing and Decision Policies
        |
        v
Intelligent Recommendation
        |
        v
LLM / RAG Interaction
        |
        v
Tourist Behaviour and Feedback
        |
        +--------------------------+
                                   |
                                   v
                         Monitoring Update
```

This architecture follows the general intelligent-control principle:

```text
Observe -> Predict -> Decide -> Act -> Evaluate -> Learn
```

## Repository Structure

```text
intelligent-tourism-control/
|
|-- app/
|   |-- backend/
|   `-- frontend/
|
|-- configs/
|   |-- forecasting/
|   |-- llm/
|   |-- monitoring/
|   |-- optimization/
|   |-- recommendation/
|   `-- reinforcement_learning/
|
|-- data/
|   |-- external/
|   |-- interim/
|   |-- processed/
|   |-- raw/
|   `-- synthetic/
|
|-- docs/
|   |-- architecture/
|   |-- experiments/
|   |-- methodology/
|   |-- publications/
|   `-- research/
|
|-- experiments/
|   |-- dynamic_pricing/
|   |-- forecasting/
|   |-- integrated_system/
|   |-- monitoring/
|   |-- rag/
|   `-- recommendation/
|
|-- models/
|   |-- forecasting/
|   |-- llm/
|   |-- recommendation/
|   `-- reinforcement_learning/
|
|-- notebooks/
|   |-- forecasting/
|   |-- llm_rag/
|   |-- monitoring/
|   |-- optimization/
|   |-- recommendation/
|   `-- reinforcement_learning/
|
|-- scripts/
|   |-- data/
|   |-- deployment/
|   |-- evaluation/
|   `-- training/
|
|-- src/
|   `-- tourism_control/
|       |-- api/
|       |-- computer_vision/
|       |-- evaluation/
|       |-- forecasting/
|       |-- knowledge_base/
|       |-- llm/
|       |-- monitoring/
|       |-- optimization/
|       |-- pricing/
|       |-- rag/
|       |-- recommendation/
|       |-- reinforcement_learning/
|       |-- robotics/
|       |-- simulation/
|       |-- uav/
|       `-- utils/
|
|-- tests/
|   |-- integration/
|   |-- system/
|   `-- unit/
|
|-- .github/
|   |-- ISSUE_TEMPLATE/
|   `-- workflows/
|
|-- .env.example
|-- .gitignore
|-- LICENSE
|-- pyproject.toml
|-- README.md
`-- requirements-dev.txt
```

## Development Philosophy

The repository is designed as a research-engineering project rather than a collection of isolated notebooks.

The intended workflow is:

```text
Exploration
    |
    v
notebooks/
    |
    v
Reusable implementation
    |
    v
src/
    |
    v
Testing
    |
    v
tests/
    |
    v
Reproducible experiments
    |
    v
experiments/
```

Research code will gradually evolve from exploratory prototypes into tested and reusable modules.

## Research Modules

The repository will be developed incrementally.

### Monitoring

Location:

```text
src/tourism_control/monitoring/
src/tourism_control/uav/
src/tourism_control/computer_vision/
```

### Forecasting

Location:

```text
src/tourism_control/forecasting/
```

### Optimization

Location:

```text
src/tourism_control/optimization/
```

### Reinforcement Learning

Location:

```text
src/tourism_control/reinforcement_learning/
```

### Dynamic Pricing

Location:

```text
src/tourism_control/pricing/
```

### Recommendation Systems

Location:

```text
src/tourism_control/recommendation/
```

### Large Language Models

Location:

```text
src/tourism_control/llm/
```

### Retrieval-Augmented Generation

Location:

```text
src/tourism_control/rag/
src/tourism_control/knowledge_base/
```

### Intelligent Robotics

Location:

```text
src/tourism_control/robotics/
```

### Integrated Simulation

Location:

```text
src/tourism_control/simulation/
experiments/integrated_system/
```

## Research Objectives

The project aims to investigate how intelligent control methods can support sustainable tourism management through:

1. adaptive sensing and monitoring,
2. forecasting of future visitor flows,
3. reinforcement learning-based decision making,
4. mathematical optimization,
5. dynamic pricing,
6. sustainable recommendation,
7. multilingual AI interaction,
8. knowledge-grounded generative AI,
9. embodied intelligent tourism assistance,
10. closed-loop integration of all system components.

## Project Status

The project is currently in **early implementation and technical specification**. A deterministic proportional-allocation heuristic and its unit tests are available. The constrained optimizer and comparative empirical evaluation remain planned.

| Workstream | Status | Current focus |
|---|---|---|
| Research architecture | Established | Maintaining clear interfaces between sensing, forecasting, optimization, recommendation, and language components |
| LLM and RAG | Design | Defining grounded interaction, retrieval, and evaluation interfaces |
| Mathematical optimization | Baseline preparation | Proportional-allocation heuristic implemented; constrained optimizer and comparative evaluation planned |
| Reinforcement learning | Planned | Comparing learned policies with optimization and heuristic baselines |
| Integrated evaluation | Protocol specified | Metric definitions, baseline comparisons, ablations, and reproducibility requirements documented; experiments planned |

Status labels describe repository maturity rather than validated scientific performance. See the [optimization milestone](docs/research/optimization-milestone.md) for the next implementation target and [CHANGELOG.md](CHANGELOG.md) for notable repository updates.

## Roadmap

- [x] Define the research vision and modular repository structure.
- [x] Document the principal scientific workstreams and intended integration path.
- [x] Specify the first optimization milestone, its assumptions, and validation criteria.
- [x] Implement a transparent proportional-allocation heuristic with feasibility tests.
- [x] Document the mathematical framework, explicit allocation model, and evaluation protocol.
- [x] Add versioned synthetic scenario fixtures and a runnable allocation evaluation report.
- [ ] Implement a deterministic optimization baseline for comparison.
- [ ] Add synthetic scenario generation, configuration files, and unit tests.
- [ ] Report feasibility, objective value, runtime, and sensitivity results.
- [ ] Connect forecasting outputs to optimization inputs through a documented interface.
- [ ] Evaluate adaptive policies against fixed and optimization-based baselines.

Roadmap items may be refined as assumptions, data availability, and experimental evidence evolve.

## Reproducibility

The project will progressively incorporate:

* reproducible environments,
* configuration-driven experiments,
* deterministic random seeds where applicable,
* automated testing,
* experiment tracking,
* model evaluation,
* dataset documentation,
* continuous integration,
* research documentation.

## License

This project is released under the MIT License.

