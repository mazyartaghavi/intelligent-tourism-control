"""Run the Stage A forecast experiment and write deterministic JSON and CSV evidence."""

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tourism_control.forecasting.baselines import DEMAND_UNIT
from tourism_control.forecasting.experiment import evaluate


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/forecasting/stage-a.json")
    parser.add_argument("--output", type=Path, required=True, help="new directory for experiment outputs")
    args = parser.parse_args()
    try:
        summary, metrics, scenario_metrics = evaluate(json.loads(args.config.read_text(encoding="utf-8")))
        summary["unit"] = DEMAND_UNIT
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / "summary.json").write_text(
            json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n"
        )
        write_csv(args.output / "metrics.csv", metrics)
        write_csv(args.output / "scenario_metrics.csv", scenario_metrics)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"forecast experiment failed: {exc}\n")
    print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()
