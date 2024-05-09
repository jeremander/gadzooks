from argparse import ArgumentParser, Namespace
import sys
from typing import ClassVar, Optional


__version__ = '0.2.9'


def error(msg: str) -> None:
    """Prints an error message and exits the program with return code 1."""
    print(f'ERROR: {msg}', file=sys.stderr)
    sys.exit(1)

def warning(msg: str) -> None:
    """Prints a warning message."""
    print(f'\033[1;33mWARNING: {msg}\x1b[0m', file=sys.stderr)


class Subcommand:
    """Configures a subcommand for the main executable."""

    @classmethod
    def configure_parser(cls, parser: ArgumentParser) -> None:
        """Configures an argument parser."""

    @classmethod
    def main(cls, args: Namespace, extra_args: Optional[list[str]] = None) -> None:
        """Runs the main logic of the subcommand, given parsed arguments."""
