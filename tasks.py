#!/usr/bin/env python3

from pathlib import Path
import invoke

ROOT = Path(__file__).parent
SHELL = "/bin/sh"


@invoke.task
def format(c, check=False):
    black_command = f"black {str(ROOT)}"
    flake_command = f"flake8 {str(ROOT)}"

    if check:
        black_command += " --check"

    print("Running Black")
    c.run(black_command, shell=SHELL)
    print("Running Flake8")
    c.run(flake_command, shell=SHELL)
