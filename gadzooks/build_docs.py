from argparse import ArgumentParser, Namespace
import binascii
from collections.abc import Sequence
import hashlib
from pathlib import Path
import subprocess
from typing import Optional

from gadzooks import Subcommand, error, warning


def xor_bytes(hashes: list[bytes]) -> bytes:
    """Computes the XOR of a collection of byte strings of the same length."""
    assert len(hashes) > 0
    arr = [0 for _ in hashes[0]]
    for h in hashes:
        for (i, b) in enumerate(arr):
            arr[i] = b ^ h[i]
    return binascii.hexlify(bytes(arr))

def get_file_checksum(paths: Sequence[Path], verbose: bool = False) -> str:
    """Computes the checksum of some files, returning it as a hex string."""
    print(f'computing checksum of {len(paths)} file(s)')
    cmd = ['sha1sum'] + list(map(str, paths))
    lines = subprocess.check_output(cmd, text=True).splitlines()
    hashes = []
    for line in lines:
        [content_hash, name] = line.split()
        name_hash = hashlib.sha1(name.encode()).hexdigest()
        hashes += list(map(binascii.unhexlify, [name_hash, content_hash]))
        if verbose:
            print(line)
    return xor_bytes(hashes).decode()


class BuildDocs(Subcommand):
    """build project documentation"""

    @classmethod
    def configure_parser(cls, parser: ArgumentParser) -> None:
        parser.add_argument('--src-docs', nargs='+', required=True, help='path(s) to input docs (will use checksum to decide whether to rebuild)')
        parser.add_argument('--checksum-file', type=Path, default='.doc-checksum', help='checksum file')
        parser.add_argument('-f', '--force', action='store_true', help='force rebuild')
        parser.add_argument('--check-only', action='store_true', help='only check whether input docs have changed (do not rebuild)')
        parser.add_argument('-v', '--verbose', action='store_true', help='print out filenames and hashes')

    @classmethod
    def main(cls, args: Namespace, extra_args: Optional[list[str]] = None) -> None:
        if not (args.check_only or extra_args):
            error('must provide: -- <BUILD_DOCS_COMMAND>')
        assert isinstance(extra_args, list)
        paths: list[Path] = []
        for path in args.src_docs:
            path = Path(path)
            if path.is_dir():
                paths.extend([p for p in path.rglob('*') if p.is_file()])
            else:
                paths.append(path)
        checksum = get_file_checksum(paths, verbose=args.verbose) if paths else None
        msg = None
        if args.force:
            pass
        elif args.checksum_file.exists():
            with open(args.checksum_file) as f:
                prev_checksum = f.read().strip()
            if checksum == prev_checksum:
                print(f'checksum matches {args.checksum_file} -- source docs are unchanged')
                return
            msg = 'source docs have changed'
        else:
            msg = 'no checksum file found'
        if msg and args.check_only:
            warning(msg)
            return
        print(msg)
        msg = 'rebuilding docs...'
        if args.force:
            msg = 'force ' + msg
        print(msg)
        print(' '.join(extra_args))
        subprocess.run(extra_args)
        if checksum:
            with open(args.checksum_file, 'w') as f:
                print(checksum, file=f)
            print(f'saved checksum to {args.checksum_file}')
