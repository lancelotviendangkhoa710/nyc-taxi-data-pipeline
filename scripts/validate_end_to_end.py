from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_COMPOSE_FILE = ROOT_DIR / "infrastructure" / "docker" / "docker-compose.local.yml"


def run_command(command: list[str], *, cwd: Path) -> int:
    print(f"$ {' '.join(command)}")
    completed = subprocess.run(command, cwd=cwd)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the NYC Taxi end-to-end validation flow in Docker."
    )
    parser.add_argument(
        "--compose-file",
        type=Path,
        default=DEFAULT_COMPOSE_FILE,
        help="Path to the Docker Compose file that wires postgres, Spark ETL, and dbt.",
    )
    parser.add_argument(
        "--keep-containers",
        action="store_true",
        help="Leave containers running after the validation flow completes.",
    )
    args = parser.parse_args()

    if shutil.which("docker") is None:
        print("Docker is not available on PATH.", file=sys.stderr)
        return 1

    if not args.compose_file.exists():
        print(f"Compose file not found: {args.compose_file}", file=sys.stderr)
        return 1

    compose_cmd = [
        "docker",
        "compose",
        "-f",
        str(args.compose_file),
        "up",
        "--build",
        "--abort-on-container-exit",
        "--exit-code-from",
        "dbt",
    ]

    try:
        exit_code = run_command(compose_cmd, cwd=ROOT_DIR)
        if exit_code != 0:
            return exit_code
        print("End-to-end validation completed successfully.")
        return 0
    finally:
        if not args.keep_containers:
            down_cmd = [
                "docker",
                "compose",
                "-f",
                str(args.compose_file),
                "down",
            ]
            run_command(down_cmd, cwd=ROOT_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
