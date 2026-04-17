"""Wallpaper subcommand — set, randomise, and inspect the current wallpaper."""
from __future__ import annotations

import json
from argparse import Namespace

from caelestia.utils.paths import wallpapers_dir
from caelestia.utils.wallpaper import get_colours_for_wall, get_wallpaper, set_random, set_wallpaper


def register_parser(subparsers) -> None:
    p = subparsers.add_parser("wallpaper", help="manage the wallpaper")
    p.set_defaults(cls=Command)
    p.add_argument("-p", "--print",    nargs="?", const=get_wallpaper(), metavar="PATH",
                   help="print the scheme for a wallpaper")
    p.add_argument("-r", "--random",   nargs="?", const=wallpapers_dir,  metavar="DIR",
                   help="switch to a random wallpaper")
    p.add_argument("-f", "--file",     help="the path to the wallpaper to switch to")
    p.add_argument("-n", "--no-filter", action="store_true", help="do not filter by size")
    p.add_argument("-t", "--threshold", default=0.8,
                   help="minimum percentage of the largest monitor size the image must exceed")
    p.add_argument("-N", "--no-smart",  action="store_true",
                   help="do not auto-change the scheme mode based on wallpaper colour")


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        if self.args.print:
            print(json.dumps(get_colours_for_wall(self.args.print, self.args.no_smart)))
        elif self.args.file:
            set_wallpaper(self.args.file, self.args.no_smart)
        elif self.args.random:
            set_random(self.args)
        else:
            print(get_wallpaper() or "No wallpaper set")
