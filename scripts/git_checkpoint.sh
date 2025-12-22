#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <type> <short> <details>" >&2
  exit 1
fi

type="$1"
short="$2"
shift 2
details="$*"

git add -A
git commit -m "${type}: ${short}" -m "${details}"
