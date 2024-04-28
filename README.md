# 🪝 Gadzooks 🪝

[![PyPI - Version](https://img.shields.io/pypi/v/py-gadzooks)](https://pypi.org/project/py-gadzooks)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://raw.githubusercontent.com/jeremander/gadzooks/main/LICENSE)

<!-- [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gadzooks.svg)](https://pypi.org/project/gadzooks) -->

-----

A collection of code maintenance tools for Python projects. These are especially useful as [pre-commit](https://pre-commit.com) hooks.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
    - [Check version consistency](#check-version)
    - [Lines of code summary](#loc-summarize)

## Installation

```text
pip install py-gadzooks
```

Requires Python 3.9 or higher.

## Usage

Once installed, `gadzooks` will be available as a command-line executable.

Different tools can be called as subcommands, which are as follows:

| Subcommand | Description |
| ---------- | ----------- |
| `check-version` | Check version consistency |
| `loc-summarize` | Summarize lines of code |

To view the help and options for a particular subcommand, do:

```text
gadzooks <SUBCOMMAND> --help
```

### `check-version`

Versions may appear in multiple locations within a project, including:

- A source file such as `__init__.py` or `__version__.py`
- Git tag
- Locally built wheels
    - Can be useful for ensuring you have remembered to build the latest version and publish it to PyPI
- An entry in a CHANGELOG file

This subcommand checks for consistency across these locations.

For now, a valid version string is required to be a sequence of three integers separated by `.`, for example, `3.7.1`. In the future, the format of version strings will become more flexible.

A valid Git tag may be a version string, optionally prefixed with `v`, for example, `v3.7.1`.

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--pkg-name PKG_NAME` | Name of package | Current directory |
| `--dist-name DIST_NAME` | Name of PyPI distribution | `<PKG_NAME>` |
| `--version-path VERSION_PATH` | Path to file where package version is defined | `<PKG_NAME>/__init__.py` |
| `--check-dist` | Check version of latest built wheel | |
| `--dist-dir DIST_DIR` | Directory where wheels are built | `dist` |
| `--changelog CHANGELOG` | Changelog file | |
| `--changelog-version-regex` | Pattern to match to find version in changelog file (`{version}` within the pattern marks the target version) | `{version}` |

### `loc-summarize`

Computes various lines-of-code metrics such as LOC (lines of code), LLOC (logical lines of code), and SLOC (source lines of code). Uses the [`radon`](https://radon.readthedocs.io/en/latest/) tool to do this.

The input argument is a path or list of paths to look for Python source files.

Example:

```text
gadzooks loc-summarize .
```

Output:

```text
Checked 4 source file(s)

LINE STATS
----------
LOC:             244
LLOC:            198
SLOC:            182
Comments:          6
Single comments:  15
Multi:            10
Blank:            37
```

## Pre-commit hooks

You can set up individual `gadzooks` subcommands to run as [pre-commit](https://pre-commit.com) hooks by configuring your `.pre-commit-config.yaml` file to point to this [Github repo](https://github.com/jeremander/gadzooks), specifying your desired subcommand by `id`, along with the command-line arguments.

You should also set `pass_filenames` to `false` to avoid passing filenames as command-line arguments by default, and `verbose` to `true` so that `gadzooks` output will be visible.

Here is an example of a section of a `.pre-commit-config.yaml` file:

```yaml
- repo: https://github.com/jeremander/gadzooks
  rev: v0.2.0
  hooks:
    - id: loc-summarize
      args: ['.']
      pass_filenames: false
      verbose: true
    - id: check-version
      args: []
      pass_filenames: false
      verbose: true
      stages: [commit, push]
```

## License

`gadzooks` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
