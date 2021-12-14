#! /usr/bin/env bash
set -e

python /app/app/pre_start.py

bash /app/app/scripts/test.sh "$@"
