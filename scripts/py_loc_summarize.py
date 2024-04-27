#!/usr/bin/env python3

import subprocess
import sys


if __name__ == '__main__':

    print('LINE STATS')
    print('----------')
    cmd = ' '.join(['radon', 'raw'] + sys.argv[1:] + ['-s'])
    lines = subprocess.check_output(cmd, text=True, shell=True).splitlines()[-11:-4]
    pairs = [line.strip().split(": ", maxsplit=1) for line in lines]
    width = len(pairs[0][1])
    for (key, val) in pairs:
        key = (key + ':').ljust(16)
        val = val.rjust(width)
        print(f'{key} {val}')
