from argparse import ArgumentParser, Namespace
from typing import ClassVar


__version__ = '0.2.0'


class Subcommand:
    """Configures a subcommand for the main executable."""

    @classmethod
    def configure_parser(cls, parser: ArgumentParser) -> None:
        """Configures an argument parser."""

    @classmethod
    def main(cls, args: Namespace) -> None:
        """Runs the main logic of the subcommand, given parsed arguments."""
