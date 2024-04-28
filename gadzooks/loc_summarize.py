from argparse import ArgumentParser, Namespace
import glob
import itertools
import subprocess

from gadzooks import Subcommand


class LinesOfCodeSummarize(Subcommand):
    """summarize lines of code in a Python project"""

    @classmethod
    def configure_parser(cls, parser: ArgumentParser) -> None:
        parser.add_argument('source_files', nargs='*', help='Python files to check')

    @classmethod
    def main(cls, args: Namespace) -> None:
        paths = list(itertools.chain.from_iterable(map(glob.glob, args.source_files)))
        if not paths:
            print('No source files to check')
            return
        cmd = ['radon', 'raw'] + list(paths) + ['-s']
        lines = subprocess.check_output(cmd, text=True).splitlines()
        num_files = sum(not line.startswith(' ') for line in lines) - 1
        assert lines[-12] == '** Total **'
        print(f'Checked {num_files} source file(s)\n')
        print('LINE STATS')
        print('----------')
        pairs = [line.strip().split(": ", maxsplit=1) for line in lines[-11:-4]]  # type: ignore[misc]
        width = len(pairs[0][1])
        for (key, val) in pairs:
            key = (key + ':').ljust(16)
            val = val.rjust(width)
            print(f'{key} {val}')
