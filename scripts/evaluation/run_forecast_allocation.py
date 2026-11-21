"""Run the forecast-to-allocation benchmark on held-out scenarios."""

import argparse
import json
from pathlib import Path

from run_forecasting import ROOT, write_csv
from tourism_control.optimization.forecast_allocation import benchmark

FORECAST_CONFIG = ROOT / "configs/forecasting/stage-a.json"
ALLOCATION_CONFIG = ROOT / "configs/optimization/forecast-allocation.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_results(output, report, timings):
    output.mkdir(parents=True, exist_ok=False)
    (output / "results.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n"
    )
    write_csv(output / "trajectories.csv", [
        {**{key: value for key, value in row.items() if not isinstance(value, dict)},
         **row["constraint_violations"]}
        for row in report["trajectories"]
    ])
    write_csv(output / "runtime.csv", timings)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forecast-config", type=Path, default=FORECAST_CONFIG)
    parser.add_argument("--allocation-config", type=Path, default=ALLOCATION_CONFIG)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    forecast_doc = read_json(args.forecast_config)
    allocation_doc = read_json(args.allocation_config)
    report, timings = benchmark(forecast_doc, allocation_doc)
    write_results(args.output, {"forecast": forecast_doc, "allocation": allocation_doc, **report}, timings)


if __name__ == "__main__":
    main()
