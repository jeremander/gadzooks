from argparse import ArgumentParser, Namespace
import sys
from typing import ClassVar


__version__ = '0.2.1'


def error(msg: str, strict: bool = True) -> None:
    """Prints an error message and exits the program with return code 1.
    If strict=False, makes it a warning and does not exit."""
    if strict:
        print(f'ERROR: {msg}', file=sys.stderr)
        sys.exit(1)
    else:
        print(f'WARNING: {msg}', file=sys.stderr)


class Subcommand:
    """Configures a subcommand for the main executable."""

    @classmethod
    def configure_parser(cls, parser: ArgumentParser) -> None:
        """Configures an argument parser."""

    @classmethod
    def main(cls, args: Namespace) -> None:
        """Runs the main logic of the subcommand, given parsed arguments."""
