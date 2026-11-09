"""Run unit tests and reproduce the committed scientific results without overwriting them."""

import argparse
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_milestone import run, text_digest, write_json

IGNORED = {"elapsed_seconds", "lp_median_elapsed_seconds", "iterations", "solver_message"}


def compare_results(expected, actual, path="root"):
    if isinstance(expected, dict):
        if expected.keys() != actual.keys():
            raise AssertionError(f"Different keys at {path}")
        for key in expected.keys() - IGNORED:
            compare_results(expected[key], actual[key], path + "." + key)
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise AssertionError(f"Different lengths at {path}")
        for i, (left, right) in enumerate(zip(expected, actual)):
            compare_results(left, right, path + f"[{i}]")
    elif type(expected) in (int, float) and type(actual) in (int, float):
        if abs(expected - actual) > 1e-7:
            raise AssertionError(f"Numerical mismatch at {path}")
    elif expected != actual:
        raise AssertionError(f"Mismatch at {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=ROOT / "reports/milestone-2026-11-09")
    parser.add_argument("--record", action="store_true", help="Write validation.json after all checks pass")
    args = parser.parse_args()
    config_path = ROOT / "configs/optimization/milestone-benchmark.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    provenance = json.loads((args.reference / "environment.json").read_text(encoding="utf-8"))
    if text_digest(config_path) != provenance["config_sha256"]:
        raise AssertionError("Configuration fingerprint mismatch")
    for relative, digest in provenance["source_sha256"].items():
        if text_digest(ROOT / relative) != digest:
            raise AssertionError(f"Source fingerprint mismatch: {relative}")
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests/unit"))
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    print(stream.getvalue())
    if not result.wasSuccessful():
        return 1
    expected = json.loads((args.reference / "results.json").read_text(encoding="utf-8"))
    compare_results(expected, run(config))
    validation = {
        "achievement_date": config["achievement_date"], "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped),
        "scientific_results_reproduced": True, "absolute_tolerance": 1e-7,
        "ignored_fields": sorted(IGNORED), "source_fingerprints_verified": True,
        "command": "python scripts/evaluation/verify_milestone.py --record",
    }
    if args.record:
        write_json(args.reference / "validation.json", validation)
    print(json.dumps(validation, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
