"""Reproduce the dated allocation milestone from versioned synthetic inputs."""

import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys
from time import perf_counter

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from tourism_control.optimization.linear import evaluate_allocation, solve_allocation
from tourism_control.optimization.proportional import allocate_capacity


def proportional(problem):
    return [allocate_capacity(d, c, b) for d, c, b in
            zip(problem["demand"], problem["capacity"], problem["budget"])]


def compare(problem, realized=None):
    optimal = solve_allocation(problem)
    start = perf_counter()
    allocation = proportional(problem)
    elapsed = perf_counter() - start
    baseline = {"allocation": allocation, "elapsed_seconds": elapsed,
                "metrics": evaluate_allocation(problem, allocation)}
    comparison = {"lp": optimal, "proportional": baseline,
                  "comparable": baseline["metrics"]["feasible"]}
    if realized is not None:
        for result in (optimal, baseline):
            result["realized_metrics"] = evaluate_allocation(problem, result["allocation"], realized)
    if comparison["comparable"] and optimal["metrics"]["objective"] > baseline["metrics"]["objective"] + 1e-6:
        raise RuntimeError("LP exceeds a feasible comparator's planning objective")
    return comparison


def stress_scenario(settings, seed, sigma):
    """Same actual trajectory and noise draw for all noise levels of each seed."""
    rng = np.random.default_rng(seed)
    shape = (settings["periods"], settings["locations"])
    actual = rng.integers(*settings["demand_range"], size=shape).astype(float)
    capacity = rng.integers(*settings["capacity_range"], size=shape).astype(float)
    penalty = rng.integers(*settings["penalty_range"], size=shape[1])
    cost = rng.uniform(*settings["operating_cost_range"], size=shape[1])
    noise = rng.normal(size=shape)
    forecast = actual * np.exp(sigma * noise - sigma**2 / 2)
    problem = {
        "demand": forecast.tolist(), "capacity": capacity.tolist(),
        "budget": (settings["budget_fraction"] * capacity.sum(axis=1)).tolist(),
        "unmet_penalty": np.tile(penalty, (shape[0], 1)).tolist(),
        "operating_cost": np.tile(cost, (shape[0], 1)).tolist(),
        "adjustment_cost": [settings["adjustment_cost"]] * shape[1],
        "initial_allocation": [0] * shape[1],
    }
    return problem, actual.tolist(), float(np.abs(forecast - actual).mean())


def paired_summary(rows, settings):
    summaries = []
    for sigma in settings["noise_sigma"]:
        group = [r for r in rows if r["noise_sigma"] == sigma]
        lp = np.array([r["lp"]["realized_metrics"]["objective"] for r in group])
        baseline = np.array([r["proportional"]["realized_metrics"]["objective"] for r in group])
        difference = baseline - lp
        rng = np.random.default_rng(settings["bootstrap_seed"])
        samples = rng.integers(0, len(group), size=(settings["bootstrap_resamples"], len(group)))
        interval = np.quantile(difference[samples].mean(axis=1), [0.025, 0.975])
        summaries.append({
            "noise_sigma": sigma, "trajectories": len(group),
            "mean_forecast_mae": float(np.mean([r["forecast_mae"] for r in group])),
            "lp_mean_realized_objective": float(lp.mean()),
            "proportional_mean_realized_objective": float(baseline.mean()),
            "mean_paired_saving": float(difference.mean()),
            "paired_saving_ci95": interval.tolist(),
            "aggregate_saving_percent": float(100 * difference.sum() / baseline.sum()),
            "lp_worse_trajectories": int(np.sum(difference < -1e-7)),
            "lp_mean_unmet": float(np.mean([r["lp"]["realized_metrics"]["unmet"] for r in group])),
            "proportional_mean_unmet": float(np.mean([r["proportional"]["realized_metrics"]["unmet"] for r in group])),
        })
    return summaries


def run(config):
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported benchmark schema")
    settings = config["stress"]
    if type(settings["replications"]) is not int or settings["replications"] < 2:
        raise ValueError("At least two independent trajectory replications are required")
    fixed = [{"id": row["id"], "problem": row["problem"], **compare(row["problem"])}
             for row in config["fixed"]]
    stress = []
    for sigma in settings["noise_sigma"]:
        for seed in range(settings["seed_start"], settings["seed_start"] + settings["replications"]):
            p, actual, error = stress_scenario(settings, seed, sigma)
            stress.append({"seed": seed, "noise_sigma": sigma, "problem": p,
                           "realized_demand": actual, "forecast_mae": error,
                           **compare(p, actual)})
    budget_sweep, adjustment_sweep = [], []
    for budget in config["sensitivity"]["budgets"]:
        p = copy.deepcopy(next(row["problem"] for row in config["fixed"] if row["id"] == "weighted_priorities"))
        p["budget"] = [budget]
        budget_sweep.append({"budget": budget, "problem": p, **compare(p)})
    for cost in config["sensitivity"]["adjustment_costs"]:
        p = copy.deepcopy(next(row["problem"] for row in config["fixed"] if row["id"] == "temporal_coupling"))
        p["adjustment_cost"] = [cost]
        adjustment_sweep.append({"adjustment_cost": cost, "problem": p, **compare(p)})
    all_pairs = fixed + stress + budget_sweep + adjustment_sweep
    summary = {
        "achievement_date": config["achievement_date"], "evidence_type": "synthetic evaluation",
        "fixed_cases": len(fixed), "stress_pairs": len(stress),
        "independent_stress_seeds": settings["replications"],
        "sensitivity_pairs": len(budget_sweep) + len(adjustment_sweep),
        "lp_solves": len(all_pairs),
        "lp_feasible": sum(r["lp"]["metrics"]["feasible"] for r in all_pairs),
        "lp_max_violation": max(r["lp"]["metrics"]["max_constraint_violation"] for r in all_pairs),
        "lp_max_primal_dual_gap": max(r["lp"]["diagnostics"]["primal_dual_gap"] for r in all_pairs),
        "lp_median_elapsed_seconds": float(np.median([r["lp"]["elapsed_seconds"] for r in all_pairs])),
        "stress": paired_summary(stress, settings),
        "unexpected_failures": 0,
    }
    return {"summary": summary, "fixed": fixed, "stress": stress,
            "budget_sweep": budget_sweep, "adjustment_sweep": adjustment_sweep}


def write_json(path, document):
    path.write_text(json.dumps(document, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def text_digest(path):
    """Canonical LF text fingerprints survive normal Git line-ending conversion."""
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def tables(report):
    lines = ["# Generated Results", "", "Synthetic evaluation; all costs use declared scenario coefficients.", "",
             "## Fixed cases", "", "| Case | LP objective | Proportional objective | LP unmet | Proportional unmet | Comparable |",
             "|---|---:|---:|---:|---:|:---:|"]
    for row in report["fixed"]:
        a, b = row["lp"]["metrics"], row["proportional"]["metrics"]
        lines.append(f"| {row['id']} | {a['objective']:.3f} | {b['objective']:.3f} | {a['unmet']:.3f} | {b['unmet']:.3f} | {'yes' if row['comparable'] else 'no: heuristic violates ramp limit'} |")
    lines += ["", "The ramp case reports both outputs for diagnosis; it is excluded from performance claims.", "",
              "## Forecast-error stress test", "", "Positive saving means lower realized objective for LP.", "",
              "| Log-noise sigma | Forecast MAE | LP objective | Proportional objective | Paired saving (95% CI) | Aggregate saving | LP worse |",
              "|---:|---:|---:|---:|---:|---:|---:|"]
    for row in report["summary"]["stress"]:
        lo, hi = row["paired_saving_ci95"]
        lines.append(f"| {row['noise_sigma']:.2f} | {row['mean_forecast_mae']:.3f} | {row['lp_mean_realized_objective']:.3f} | {row['proportional_mean_realized_objective']:.3f} | {row['mean_paired_saving']:.3f} [{lo:.3f}, {hi:.3f}] | {row['aggregate_saving_percent']:.2f}% | {row['lp_worse_trajectories']}/{row['trajectories']} |")
    lines += ["", "Intervals resample whole paired trajectories, separately at each noise level. They are not simultaneous intervals or field-performance guarantees.", "",
              "## Numerical validation", ""]
    s = report["summary"]
    lines += [f"- Successful LP solves: {s['lp_solves']}.",
              f"- Allocations feasible at 1e-7 tolerance: {s['lp_feasible']}.",
              f"- Maximum constraint violation: {s['lp_max_violation']:.3g}.",
              f"- Maximum absolute primal-dual gap: {s['lp_max_primal_dual_gap']:.3g}.",
              "- Unexpected solve failures: 0 (the runner aborts if one occurs).", ""]
    return "\n".join(lines)


def plots(report, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    matplotlib.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                               "axes.spines.top": False, "axes.spines.right": False,
                               "svg.hashsalt": "allocation-milestone-v1"})
    teal, slate, orange = "#087f8c", "#64748b", "#c46a28"
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    fig.set_facecolor("#f8fafc")
    fig.suptitle("CAPACITY ALLOCATION  |  Reproducible milestone\n09 November 2026 · Synthetic evaluation", fontsize=20, fontweight="bold", color="#102a43")
    selected = [r for r in report["fixed"] if r["id"] in {"uniform_priorities", "weighted_priorities", "expensive_service"}]
    pos = np.arange(len(selected))
    ax = axes[0, 0]
    ax.bar(pos - .18, [r["proportional"]["metrics"]["objective"] for r in selected], .36, label="Proportional", color=slate)
    ax.bar(pos + .18, [r["lp"]["metrics"]["objective"] for r in selected], .36, label="Linear program", color=teal)
    ax.set_xticks(pos, ["Uniform priorities", "Weighted priorities", "Expensive service"])
    ax.set_ylabel("Planning objective (lower is better)")
    ax.set_title("A  |  Same model, different allocation rules", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    ax = axes[0, 1]
    rows = report["summary"]["stress"]
    mean = np.array([r["mean_paired_saving"] for r in rows])
    ci = np.array([r["paired_saving_ci95"] for r in rows])
    ax.errorbar([r["noise_sigma"] for r in rows], mean,
                yerr=np.vstack((mean-ci[:, 0], ci[:, 1]-mean)), color=teal, marker="o", capsize=5, lw=2)
    ax.axhline(0, color=slate, lw=1)
    ax.set_xlabel("Forecast log-noise scale (sigma)")
    ax.set_ylabel("Realized objective saving: proportional − LP")
    ax.set_title("B  |  Forecast errors erode the advantage", loc="left", fontweight="bold")
    ax.text(.04, .06, f"{rows[0]['trajectories']} paired trajectories per level\n95% bootstrap intervals", transform=ax.transAxes, color=slate)
    ax = axes[1, 0]
    rows = report["budget_sweep"]
    for method, label, color in [("proportional", "Proportional", slate), ("lp", "Linear program", teal)]:
        ax.plot([r["budget"] for r in rows], [r[method]["metrics"]["objective"] for r in rows], "o-", label=label, color=color)
    ax.set_xlabel("Shared service-capacity budget")
    ax.set_ylabel("Planning objective")
    ax.set_title("C  |  Budget sensitivity", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    ax = axes[1, 1]
    rows = report["adjustment_sweep"]
    ax.plot([r["adjustment_cost"] for r in rows], [r["lp"]["metrics"]["total_change"] for r in rows], "o-", color=teal, label="Allocation change")
    ax.plot([r["adjustment_cost"] for r in rows], [r["lp"]["metrics"]["unmet"] for r in rows], "s--", color=orange, label="Unmet demand")
    ax.set_xlabel("Penalty per changed service unit")
    ax.set_ylabel("Service-capacity units")
    ax.set_title("D  |  Stability has a service trade-off", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    for ax in axes.ravel():
        ax.grid(axis="y", alpha=.15)
        ax.set_axisbelow(True)
    output.mkdir(parents=True, exist_ok=True)
    figure_path = output / "results-overview.svg"
    fig.savefig(figure_path, metadata={"Date": None})
    figure_path.write_text("\n".join(line.rstrip() for line in
                                    figure_path.read_text(encoding="utf-8").splitlines()) + "\n",
                           encoding="utf-8")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/optimization/milestone-benchmark.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/milestone-2026-11-09")
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    report = run(config)
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output / "results.json", report)
    write_json(args.output / "summary.json", report["summary"])
    (args.output / "results.md").write_text(tables(report), encoding="utf-8")
    csv_rows = []
    for suite in ("fixed", "stress", "budget_sweep", "adjustment_sweep"):
        for index, row in enumerate(report[suite]):
            for method in ("lp", "proportional"):
                metrics = row[method].get("realized_metrics", row[method]["metrics"])
                csv_rows.append({"suite": suite, "case": row.get("id", index),
                                 "seed": row.get("seed", ""), "noise_sigma": row.get("noise_sigma", ""),
                                 "method": method, "objective": metrics["objective"],
                                 "weighted_unmet": metrics["weighted_unmet"],
                                 "operating_cost": metrics["operating_cost"],
                                 "adjustment_cost": metrics["adjustment_cost"], "unmet": metrics["unmet"],
                                 "served": metrics["served"], "max_violation": metrics["max_constraint_violation"],
                                 "feasible": metrics["feasible"], "elapsed_seconds": row[method]["elapsed_seconds"]})
    with (args.output / "metrics.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)
    from scipy.optimize._highspy import _core
    import matplotlib
    tracked = ["src/tourism_control/optimization/linear.py", "src/tourism_control/optimization/proportional.py",
               "scripts/evaluation/run_milestone.py", "requirements-milestone.txt",
               "requirements-milestone-lock.txt", "scripts/evaluation/verify_milestone.py"]
    tracked += [path.relative_to(ROOT).as_posix() for path in sorted((ROOT / "tests/unit").glob("test_*.py"))]
    provenance = {"python": platform.python_version(), "platform": platform.system(),
                  "architecture": platform.machine(), "processor": platform.processor(),
                  "numpy": np.__version__, "scipy": scipy.__version__, "matplotlib": matplotlib.__version__,
                  "highs": ".".join(str(getattr(_core, "HIGHS_VERSION_" + k)) for k in ("MAJOR", "MINOR", "PATCH")),
                  "solver_method": "highs-ds", "presolve": True, "solver_tolerance": 1e-9,
                  "hash_convention": "SHA-256 of UTF-8 text normalized to LF line endings",
                  "config_sha256": text_digest(args.config),
                  "source_sha256": {p: text_digest(ROOT / p) for p in tracked},
                  "runtime_note": "Model validation, construction and solve wall time; single-run descriptive timings, not a solver speed benchmark."}
    write_json(args.output / "environment.json", provenance)
    if not args.no_plots:
        plots(report, args.output / "figures")
    print(tables(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
