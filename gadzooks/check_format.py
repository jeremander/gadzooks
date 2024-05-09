from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
import re
import shutil
import subprocess
import sys
from typing import Optional, TypedDict

from gadzooks import Subcommand, error


Header = list[str]
Section = list[str]
SectionGroup = tuple[Header, list[Section]]


class FormatterInfo(TypedDict):
    """Info related to a code formatter command."""
    args: str
    success: list[int]


FORMATTERS: dict[str, FormatterInfo] = {
    'black': {
        'args': 'black',
        'success': [0],
    },
    'ruff': {
        'args': 'ruff format',
        'success': [0, 1],
    },
    'yapf': {
        'args': 'yapf --recursive',
        'success': [0, 1],
    },
}

SECTION_REGEX = re.compile(r'@@\s+[-+]?\d+,\d+\s+[-+]\d+,\d+\s+@@')



def get_diff_section_groups(diff: str) -> list[SectionGroup]:
    """Splits up a diff into section groups."""
    groups = []
    header: Header = []
    sections: list[Section] = []
    section: Section = []
    for line in diff.splitlines():
        if line.startswith('---'):  # start a new group
            if sections or header:
                if section:
                    sections.append(list(section))
                    section.clear()
                groups.append((list(header), list(sections)))
                header.clear()
                sections.clear()
            header.append(line)
        elif SECTION_REGEX.match(line):  # section boundary
            if section:
                sections.append(list(section))
                section.clear()
            section.append(line)
        elif section:  # middle of a section
            section.append(line)
        else:  # middle of group header
            header.append(line)
    if section:
        sections.append(section)
    if sections:
        groups.append((header, sections))
    return groups


@dataclass
class DiffFilter:
    """Class for filtering diffs to exclude certain regular expressions."""
    ignore_patterns: list[str]

    def __post_init__(self) -> None:
        self._ignore_regexes = [re.compile(pattern) for pattern in self.ignore_patterns]

    def check_line(self, line: str) -> bool:
        """If the given line starts with + or -, returns True if the remainder does not match one of the ignore patterns.
        Otherwise, returns False."""
        if line.startswith('-') or line.startswith('+'):
            return not any(regex.fullmatch(line[1:]) for regex in self._ignore_regexes)
        return False

    def check_section(self, section: Section) -> bool:
        """Given a diff section, returns True if at least one line beginning with + or - does not match one of the ignore patterns."""
        return any(self.check_line(line) for line in section)

    def filter_group(self, group: SectionGroup) -> Optional[SectionGroup]:
        """Given a section group, returns the filtered group (removing sections with only ignore patterns), or None if there are no remaining sections."""
        (header, sections) = group
        sections = list(filter(self.check_section, sections))
        return (header, sections) if sections else None


class CheckFormat(Subcommand):
    """check code formatting"""

    @classmethod
    def configure_parser(cls, parser: ArgumentParser) -> None:
        parser.add_argument('files', nargs='+', help='sources files to check')
        parser.add_argument('--formatter', choices=list(FORMATTERS), default='black', help='name of formatter executable')
        parser.add_argument('--ignore-patterns', nargs='+', help='regular expression(s) to ignore in diffs')

    @classmethod
    def main(cls, args: Namespace, extra_args: Optional[list[str]] = None) -> None:
        if not shutil.which(args.formatter):
            error(f'could not locate code formatter {args.formatter!r}')
        fmt_data = FORMATTERS[args.formatter]
        cmd = fmt_data['args'].split() + [*args.files, '--diff', *(extra_args or [])]
        print('Checking code format...\n' + ' '.join(cmd), file=sys.stderr)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        if result.returncode not in fmt_data['success']:
            error(result.stderr)
        groups = get_diff_section_groups(result.stdout)
        diff_filter = DiffFilter(args.ignore_patterns or [])
        groups = [filtered for group in groups if (filtered := diff_filter.filter_group(group))]
        if groups:
            for (header, sections) in groups:
                print('\n'.join(header))
                for section in sections:
                    print('\n'.join(section))
            sys.exit(1)
        print('No changes.', file=sys.stderr)
