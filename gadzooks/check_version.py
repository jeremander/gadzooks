from argparse import ArgumentParser, Namespace
from pathlib import Path
import re
import subprocess
import sys
from typing import Optional

from gadzooks import Subcommand


VERSION_PATTERN = r'\d+\.\d+\.\d+'
VERSION_REGEX = re.compile(VERSION_PATTERN)


def error(msg: str, strict: bool = True) -> None:
    """Prints an error message and exits the program with return code 1.
    If strict=False, makes it a warning and does not exit."""
    if strict:
        print(f'ERROR: {msg}', file=sys.stderr)
        sys.exit(1)
    else:
        print(f'WARNING: {msg}', file=sys.stderr)

def parse_version_str(version: str) -> tuple[int, ...]:
    """Parses a version string into an integer tuple."""
    return tuple(map(int, version.split('.')))

def get_latest_tag() -> Optional[str]:
    """Gets the latest git tag, or None if there is no tag."""
    try:
        return subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0'], text=True).strip()
    except subprocess.CalledProcessError:
        return None

def check_tag_version(strict: bool = False) -> Optional[str]:
    """Checks that the latest tag is a valid version (for now, other tags are not allowed).
    Returns the version as a string, or None if there is no tag.
    If strict=True, requires the tag be a valid version."""
    latest_tag = get_latest_tag()
    if latest_tag:
        print(f'Latest tag:           {latest_tag}')
        tag_version = latest_tag.lstrip('v')
        if not VERSION_REGEX.match(tag_version):
            error(f'tag {latest_tag!r} is not a valid version', strict=strict)
        print(f'Tag version:          {tag_version}')
        return tag_version
    error('No tags exist.', strict=strict)
    return None

def get_pkg_version(path: Path) -> Optional[str]:
    """Finds the first occurrence of a version string in the given file.
    A version string is assumed to be the right-hand side of an expression like `version = '3.7.1'` or `__version__ = '2.3.4'`."""
    with open(path) as f:
        contents = f.read()
    regex = re.compile(r'\_*version\_*\s*=\s*[\'\"](' + VERSION_PATTERN + ')')
    if (match := regex.search(contents)):
        return match.group(1)
    return None

def check_pkg_version(version_path: Path, version: Optional[str], strict: bool = False) -> str:
    """Checks that the version of the Python package is a valid version string.
    If strict=True, also requires this version to match the target version.
    Returns the package version."""
    pkg_version = get_pkg_version(version_path)
    if pkg_version is None:
        error(f'no package version found in {version_path}')
    assert isinstance(pkg_version, str)
    print(f'Package version:      {pkg_version}')
    if not VERSION_REGEX.match(pkg_version):
        error(f'package version string {pkg_version!r} is not a valid version')
    if version is None:
        error('no version tag to compare with package version', strict=strict)
    if pkg_version != version:
        error(f'mismatch between tag version ({version}) and package version ({pkg_version}) -- remember to update tag', strict=strict)
    return pkg_version

def get_latest_built_version(pkg_name: str, dist_dir: str = 'dist') -> Optional[str]:
    """Given the name of the Python package and a dist directory where wheels are built, returns the version string of the latest built wheel."""
    dist_path = Path(dist_dir)
    if not dist_path.is_dir():
        return None
    max_version: Optional[tuple[int, ...]] = None
    wheel_pattern = f'{pkg_name}-*.whl'
    for path in dist_path.glob(wheel_pattern):
        if (match := VERSION_REGEX.search(path.name)):
            version = parse_version_str(match.group())
            max_version = version if (max_version is None) else max(version, max_version)
    return None if (max_version is None) else '.'.join(map(str, max_version))

def check_latest_built_version(version: str, pkg_name: str, dist_dir: str, strict: bool = False) -> None:
    """Checks the latest built wheel in dist_dir matches the target version."""
    built_version = get_latest_built_version(pkg_name, dist_dir=dist_dir)
    if built_version:
        print(f'Latest built version: {built_version}')
    if (not built_version) or (built_version != version):
        error(f'latest version has not been built in {dist_dir} -- remember to build & publish v{version}', strict=strict)

def check_changelog_version(version: str, changelog: Path, changelog_version_regex: str) -> None:
    """Checks that the changelog file contains a line matching a pattern that corresponds to the target version."""
    pattern = changelog_version_regex.format(version=version)
    has_pattern = False
    with open(changelog) as f:
        for line in f:
            if re.search(pattern, line):
                has_pattern = True
                break
    if has_pattern:
        print(f'Changelog line:       {line}')
    else:
        error(f'{changelog} may not be up-to-date, does not contain a line matching:\n\t{pattern}')


class CheckVersion(Subcommand):
    """check version consistency in a Python project"""

    @classmethod
    def configure_parser(cls, parser: ArgumentParser) -> None:
        parser.add_argument('--pkg-name', help='name of the Python package')
        parser.add_argument('--version-path', type=Path, help='path to file containing current version')
        parser.add_argument('--check-tag', action='store_true', help='check that the latest tag is a valid version')
        parser.add_argument('--check-dist', action='store_true', help='check version of latest built wheel')
        parser.add_argument('--dist-dir', help='directory where package wheels are built')
        parser.add_argument('--changelog', help='changelog file')
        parser.add_argument('--changelog-version-regex', default='{version}', help='pattern to match to find version in changelog file ("{version}" within the pattern marks the target version')

    @classmethod
    def main(cls, args: Namespace) -> None:
        # by default, assume root directory name matches the package name
        pkg_name = args.pkg_name or Path.cwd().name.replace('-', '_')
        tag_version = check_tag_version(strict=args.check_tag)
        # by default, assume the package directory is a subdirectory with the package name
        version_path = args.version_path or Path(pkg_name) / '__init__.py'
        pkg_version = check_pkg_version(version_path, tag_version, strict=args.check_tag)
        if args.check_dist or args.dist_dir:
            dist_dir = args.dist_dir or 'dist'
            check_latest_built_version(pkg_version, pkg_name, dist_dir, strict=args.check_dist)
        if args.changelog:
            check_changelog_version(pkg_version, args.changelog, args.changelog_version_regex)
