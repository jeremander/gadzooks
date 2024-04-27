#!/usr/bin/env python3

import argparse
from pathlib import Path
import re
import subprocess
import sys
from typing import Optional


VERSION_REGEX = re.compile(r'\d+\.\d+\.\d+')

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
        print(f'Latest version:       {tag_version}')
        return tag_version
    error('No tags exist.', strict=strict)
    return None

def check_pkg_version(version: Optional[str], strict: bool = False) -> str:
    """Checks that the version of the Python package is a valid version string.
    If strict=True, also requires this version to match the target version.
    Returns the package version."""
    # TODO: check for version pattern in specific file
    pkg_version = subprocess.check_output(['hatch', 'version'], text=True).strip()
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
    if not dist_path.exists():
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
        error(f'latest version has not been built -- remember to build & publish v{version}', strict=strict)

def check_changelog_version(version: str, changelog: Path, changelog_version_regex: str) -> None:
    """Checks that the changelog file contains a line matching a pattern that corresponds to the target version."""
    pattern_regex = re.compile(changelog_version_regex.format(version))
    # url_regex = re.compile(r'\[' + str(tag_version) + r'\]:\s*\w+')
    has_pattern = False
    with open(args.changelog) as f:
        for line in f:
            if pattern_regex.search(line):
                has_pattern = True
                break
    if has_pattern:
        print('Changelog: OK')
    else:
        error(f'{args.changelog} may not be up-to-date, does not contain a line matching:\n\t{pattern_regex}')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('pkg_name', help='name of the Python package')
    parser.add_argument('--check-tag', action='store_true', help='check that the latest tag is a valid version')
    parser.add_argument('--check-dist', action='store_true', help='check version of latest built wheel')
    parser.add_argument('--dist-dir', default='dist', help='directory where package wheels are built')
    parser.add_argument('--changelog', help='changelog file')
    parser.add_argument('--changelog-version-regex', default='{version}', help='pattern to match to find version in changelog file ("{version}" within the pattern marks the target version')
    args = parser.parse_args()

    tag_version = check_tag_version(strict=args.check_tag)

    pkg_version = check_pkg_version(tag_version, strict=args.check_tag)

    if args.check_dist:
        check_latest_built_version(pkg_version, args.pkg_name, args.dist_dir)

    if args.changelog:
        check_changelog_version(pkg_version, args.changelog, args.changelog_version_regex)
