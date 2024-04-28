#!/usr/bin/env python3

import argparse
from typing import cast

from gadzooks import Subcommand, __version__
from gadzooks.check_version import CheckVersion
from gadzooks.loc_summarize import LinesOfCodeSummarize


SUBCOMMANDS: dict[str, type[Subcommand]] = {
    'check-version': CheckVersion,
    'loc-summarize': LinesOfCodeSummarize,
}

def main() -> None:
    """Main entry point for gadzooks executable."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true', help='print version number')
    subparsers = parser.add_subparsers(dest='subcommand')
    for (name, cls) in SUBCOMMANDS.items():
        doc = cast(str, cls.__doc__)
        descr = doc[0].upper() + doc[1:] + '.'
        subparser = subparsers.add_parser(name, description=descr, help=doc)
        cls.configure_parser(subparser)
    args = parser.parse_args()
    if args.version:
        print(__version__)
        return
    if not args.subcommand:
        parser.error('the following arguments are required: subcommand')
    SUBCOMMANDS[args.subcommand].main(args)


if __name__ == '__main__':
    main()
