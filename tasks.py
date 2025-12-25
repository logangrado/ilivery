#!/usr/bin/env python3

from pathlib import Path

import invoke

ROOT = Path(__file__).parent
SHELL = "/bin/sh"


@invoke.task
def format(c, check=False):
    dirs = ["src", "tests"]
    dirs = " ".join([str(ROOT / d) for d in dirs])
    print(dirs)
    format_command = f"ruff format {dirs}"
    lint_command = f"ruff check {dirs}"

    if check:
        format_command += " --check"
    else:
        lint_command += " --fix"

    print("Formatting")
    print(format_command)
    c.run(format_command, shell=SHELL)
    print("Linting")
    print(lint_command)
    c.run(lint_command, shell=SHELL)
