"""Clipboard subcommand — search and manage clipboard history via cliphist."""
from __future__ import annotations

import subprocess
from argparse import Namespace


def register_parser(subparsers) -> None:
    p = subparsers.add_parser("clipboard", help="open clipboard history")
    p.set_defaults(cls=Command)
    p.add_argument("-d", "--delete", action="store_true", help="delete from clipboard history")


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        clip = subprocess.check_output(["cliphist", "list"])

        if self.args.delete:
            args = ["--prompt=del > ", "--placeholder=Delete from clipboard"]
        else:
            args = ["--placeholder=Type to search clipboard"]

        chosen = subprocess.check_output(["fuzzel", "--dmenu", *args], input=clip)

        if self.args.delete:
            subprocess.run(["cliphist", "delete"], input=chosen)
        else:
            decoded = subprocess.check_output(["cliphist", "decode"], input=chosen)
            subprocess.run(["wl-copy"], input=decoded)
