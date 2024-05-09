# 🪝 Gadzooks 🪝

[![PyPI - Version](https://img.shields.io/pypi/v/py-gadzooks)](https://pypi.org/project/py-gadzooks)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://raw.githubusercontent.com/jeremander/gadzooks/main/LICENSE)

<!-- [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gadzooks.svg)](https://pypi.org/project/gadzooks) -->

-----

A collection of code maintenance tools for Python projects. These are especially useful as [pre-commit](https://pre-commit.com) hooks.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
    - [Lines of code summary](#loc-summarize)
    - [Check version consistency](#check-version)
    - [Check code formatting](#check-format)
    - [Build documentation](#build-docs)

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
| `build-docs` | Build project documentation |
| `check-format` | Check code formatting |
| `check-version` | Check version consistency |
| `loc-summarize` | Summarize lines of code |

To view the help and options for a particular subcommand, do:

```text
gadzooks <SUBCOMMAND> --help
```

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
| `--check-tag` | Check that latest tag is valid | |
| `--check-dist` | Check version of latest built wheel | |
| `--dist-dir DIST_DIR` | Directory where wheels are built | `dist` |
| `--changelog CHANGELOG` | Changelog file | |
| `--changelog-version-regex` | Pattern to match to find version in changelog file (`{version}` within the pattern marks the target version) | `{version}` |

### `check-format`

Runs an installed code formatter on source files. Currently supported formatters (for Python code only) are:

- [Black](https://black.readthedocs.io/en/stable/)
- [Ruff](https://docs.astral.sh/ruff/formatter)
- [Yapf](https://github.com/google/yapf)

Example usage:

```text
gadzooks check-format . --formatter black --ignore-patterns "\s*" -- --line-length 120 --skip-string-normalization
```

If `--` is present, the arguments that come before it are `gadzooks`' arguments; those that come after it are passed to the formatter program.

`check-format` does not (by default) edit the code in place, but rather prints out a stream of _diffs_ indicating what formatting changes would be made. The user may choose to apply the changes or not.

The program exits with return code 1 if there are any changes, and 0 otherwise.

| Option | Description | Default |
| ------ | ----------- | ------- |
| (positional) | Files or directories to check | (required) |
| `--formatter` | Formatter program (`black`, `ruff`, or `yapf`) | `black` |
| `--ignore-patterns` | One or more regular expressions that will be ignored in the diffs (e.g. `"\s*"` ignores changes where whitespace lines are added or removed) | |

### `build-docs`

Runs a command to build docs within your project.

A typical pattern is to build documentation from template files such as Markdown, then save them out as HTML. Often this is done external to source control via some CI process which builds and deploys docs to a website. However, in some cases you may want to commit the built documentation to your Git repo. This is an easy step to forget, so `gadzooks` let you make the action into a `pre-commit` hook.

Example usage:

```text
gadzooks build-docs --src-docs docs -- make docs
```

The `--src-docs` option lets you specify which files are the source docs to be built. `gadzooks` will first check if any of these files has changed since the last time the docs were built (by means of a saved checksum file). If none has changed, it will do nothing. Otherwise, it will call the command following the final `--` (in the example above, `make docs`).

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--src-docs SRC_DOCS` | Files or directories containing source docs |  |
| `--checksum-file CHECKSUM_FILE` | File where SHA-1 checksum is stored | `.doc-checksum` |

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
      # before pushing, require the git tag match the package version
    - id: check-version
      args: ['--check-tag']
      pass_filenames: false
      verbose: true
      stages: [push]
```

## License

`gadzooks` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
