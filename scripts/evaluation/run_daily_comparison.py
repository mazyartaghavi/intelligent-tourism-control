"""Train and compare daily policies on disjoint, seeded synthetic scenarios."""

import argparse
from pathlib import Path

from run_forecast_allocation import ROOT, FORECAST_CONFIG, ALLOCATION_CONFIG, read_json, write_results
from tourism_control.control.experiment import compare


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forecast-config", type=Path, default=FORECAST_CONFIG)
    parser.add_argument("--allocation-config", type=Path, default=ALLOCATION_CONFIG)
    parser.add_argument("--control-config", type=Path, default=ROOT / "configs/control/stage-e.json")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    forecast_doc, allocation_doc, control_doc = (
        read_json(path) for path in (args.forecast_config, args.allocation_config, args.control_config)
    )
    report, timings = compare(forecast_doc, allocation_doc, control_doc)
    write_results(args.output, {"forecast": forecast_doc, "allocation": allocation_doc,
                                "control": control_doc, **report}, timings)


if __name__ == "__main__":
    main()
