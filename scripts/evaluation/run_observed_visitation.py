"""Forecast monthly park visits and score counterfactual service allocations."""

import argparse
import csv
from hashlib import sha256
import json
from math import fsum, sqrt
from pathlib import Path
from statistics import median

from run_forecast_allocation import ROOT, read_json, write_csv
from tourism_control.optimization.forecast_allocation import AllocationSettings, proportional_plan, score_path
from tourism_control.optimization.linear import solve_allocation

PARKS = ("ACAD", "SHEN", "GRSM")
START_YEAR, VALIDATION_YEAR, TEST_YEAR, END_YEAR = 2010, 2019, 2022, 2026
METHODS = ("persistence", "seasonal_naive", "seasonal_mean")
SOURCE_SHA256 = "284ab33b15e9a817948cba4663ed33748ba24dbbc36b750be2b2cfbb662fe912"
DATA = ROOT / "data/processed/nps-recreation-visits-2010-2025.csv"


def periods(start, stop):
    return [(year, month) for year in range(start, stop) for month in range(1, 13)]


def extract(source, output):
    with source.open("rb") as stream:
        from hashlib import file_digest
        if file_digest(stream, "sha256").hexdigest() != SOURCE_SHA256:
            raise ValueError("upstream CSV checksum mismatch")
    seen = {}
    with source.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["Statistic"] == "TRV" and row["UnitCode"] in PARKS:
                year = int(row["Year"])
                if START_YEAR <= year < END_YEAR:
                    key = year, int(row["Month"]), row["UnitCode"]
                    if key in seen:
                        raise ValueError(f"duplicate source row {key}")
                    seen[key] = int(row["Value"])
    rows = [{"year": year, "month": month, **{park: seen[year, month, park] for park in PARKS}}
            for year, month in periods(START_YEAR, END_YEAR)]
    if output.exists():
        raise FileExistsError(output)
    write_csv(output, rows)


def load_panel(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["year", "month", *PARKS]:
            raise ValueError("expected year, month and park columns in the declared order")
        rows = list(reader)
    if [(int(row["year"]), int(row["month"])) for row in rows] != periods(START_YEAR, END_YEAR):
        raise ValueError("expected every month once and in chronological order")
    values = [[int(row[park]) for park in PARKS] for row in rows]
    if any(value < 0 for row in values for value in row):
        raise ValueError("visit counts must be nonnegative")
    return values


def predict(history, origin, method):
    """Use only pre-sliced records available at the start of the quarter."""
    if len(history) != origin - 1:
        raise ValueError("history must end two months before the forecast origin")
    if method == "persistence":
        return [history[-1][:] for _ in range(3)]
    if method == "seasonal_naive":
        return [history[origin + step - 12][:] for step in range(3)]
    if method != "seasonal_mean":
        raise ValueError("unknown forecast method")
    return [[fsum(history[origin + step - lag][site] for lag in (12, 24, 36)) / 3
             for site in range(len(PARKS))] for step in range(3)]


def metric(errors):
    return {"n": len(errors), "mae": fsum(map(abs, errors)) / len(errors),
            "rmse": sqrt(fsum(error ** 2 for error in errors) / len(errors))}


def benchmark(values, settings):
    start_validation = (VALIDATION_YEAR - START_YEAR) * 12
    start_test = (TEST_YEAR - START_YEAR) * 12
    score_rows, test_forecasts = [], {}
    selected = None
    for split, start, stop in (("validation", start_validation, start_test), ("test", start_test, len(values))):
        overall = {}
        for method in METHODS:
            predictions = [row for origin in range(start, stop, 3)
                           for row in predict(values[:origin - 1], origin, method)]
            errors = [[predicted - actual for predicted, actual in zip(pred, truth)]
                      for pred, truth in zip(predictions, values[start:stop])]
            overall[method] = metric([value for row in errors for value in row])
            for site, park in enumerate(PARKS):
                score_rows.append({"split": split, "method": method, "park": park,
                                   **metric([row[site] for row in errors])})
            score_rows.append({"split": split, "method": method, "park": "all", **overall[method]})
            if split == "test":
                test_forecasts[method] = predictions
        if split == "validation":
            selected = min(METHODS, key=lambda name: (overall[name]["mae"], name))

    actual = values[start_test:]
    training = values[:start_validation]
    seasonal_limits = [[1.1 * median(row[site] for row in training[month::12])
                        for site in range(len(PARKS))] for month in range(12)]
    limits = [seasonal_limits[month % 12] for month in range(len(actual))]
    variants = {"proportional_selected": (selected, proportional_plan)}
    variants.update({f"lp_{method}": (method, lambda problem: solve_allocation(problem)["allocation"])
                     for method in METHODS})
    rows = []
    for policy, (method, planner) in variants.items():
        forecast = test_forecasts[method]
        initial = [0] * len(PARKS)
        previous = initial
        path = []
        for offset in range(0, len(actual), 3):
            boundary = offset + 3
            problem = settings.problem(forecast[offset:boundary], limits[offset:boundary], previous)
            allocation = planner(problem)
            path.extend(allocation)
            previous = allocation[-1]
        for year in range(TEST_YEAR, END_YEAR):
            offset = (year - TEST_YEAR) * 12
            cut = slice(offset, offset + 12)
            prior = initial if offset == 0 else path[offset - 1]
            result = score_path(settings.problem(forecast[cut], limits[cut], prior), path[cut], actual[cut])
            if not result["feasible"]:
                raise RuntimeError(f"infeasible annual record: {policy}, {year}")
            rows.append({"policy": policy, "year": year, **result})
    return selected, score_rows, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", type=Path, help="extract the pinned upstream CSV instead of benchmarking")
    parser.add_argument("--panel", type=Path, default=DATA)
    parser.add_argument("--output", type=Path, help="new output directory for benchmark results")
    args = parser.parse_args()
    if args.source_csv:
        extract(args.source_csv, args.panel)
        return
    if args.output is None:
        parser.error("--output is required when benchmarking")
    allocation_doc = read_json(ROOT / "configs/optimization/forecast-allocation.json")
    settings = AllocationSettings.from_document(allocation_doc, len(PARKS))
    selected, metrics, rows = benchmark(load_panel(args.panel), settings)
    args.output.mkdir(parents=True, exist_ok=False)
    write_csv(args.output / "forecast_metrics.csv", metrics)
    write_csv(args.output / "annual_allocation.csv", [
        {**{k: v for k, v in row.items() if k != "constraint_violations"}, **row["constraint_violations"]}
        for row in rows
    ])
    summary = {"source_doi": "10.57830/2317666", "source_sha256": SOURCE_SHA256,
               "panel_sha256": sha256(args.panel.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
               "selected_by_validation_mae": selected, "allocation_settings": allocation_doc,
               "annual_allocation": rows}
    (args.output / "results.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n",
                                             encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
