#!/usr/bin/env sh

cat "$HOME/.local/state/caelestia/sequences.txt" 2>/dev/null

exec "$@"