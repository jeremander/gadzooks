#!/usr/bin/env bash

echo "LINE STATS"
echo "----------"
radon raw $1 -s | tail -n 11 | head -n 7 | awk '{$1=$1};1'
