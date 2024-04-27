#!/usr/bin/env bash

echo "LINE STATS"
echo "----------"
radon raw $1 -s | tail -n 11 | head -n 7 | python3 -c '
import sys
pairs = [line.strip().split(": ", maxsplit=1) for line in sys.stdin]
pairs = [((key + ":").ljust(16), val) for (key, val) in pairs]
width = len(pairs[0][1])
for (key, val) in pairs:
    print(f"{key} {val.rjust(width)}")'
