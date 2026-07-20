"""Reproduce the full LLM-Powered Query Monitoring evaluation.

Usage:
    python reproduce.py                    # Full pipeline (datasets → report)
    python reproduce.py --skip-datasets   # Use existing datasets
    python reproduce.py --help

Output: updated data/cost_analysis_report.md, data/query_history.db
"""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parent / "scripts"

def run_step(label: str, script_name: str, *args: str) -> None:
    print(f"\n{'='*60}")
    print(f"  [{label}] Running {script_name}...")
    print(f"{'='*60}")
    script = SCRIPTS / script_name
    if not script.exists():
        print(f"  [SKIP] {script} not found")
        return
    result = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"  [FAIL] {script_name} exited with code {result.returncode}")
        sys.exit(result.returncode)
    print(f"  [OK] {script_name} completed")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reproduce the full LLM-Powered Query Monitoring evaluation"
    )
    parser.add_argument(
        "--skip-datasets",
        action="store_true",
        help="Skip dataset download (use existing data/raw)",
    )
    args = parser.parse_args()

    print("LLM-Powered Query Monitoring - Reproduction Pipeline")
    print(f"   Python: {sys.version}")

    if not args.skip_datasets:
        run_step("1/6", "maintain_datasets.py", "sync")

    run_step("2/6", "create_db.py")
    run_step("3/6", "create_query_workload.py")
    run_step("4/6", "execute_query_workload.py")
    run_step("5/6", "llm_analysis.py")
    run_step("6/6", "generate_report.py")

    print(f"\n{'='*60}")
    print(f"  Reproduction complete.")
    print(f"  Report: data/cost_analysis_report.md")
    print(f"  Database: data/query_history.db")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
