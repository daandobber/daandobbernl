#!/bin/bash
export BLUESKY_HANDLE="bluesky@daandobber.nl"

if [ -z "${BLUESKY_APP_PASSWORD:-}" ]; then
	echo "BLUESKY_APP_PASSWORD is niet ingesteld" >&2
	exit 1
fi

cd "$(dirname "$0")"
venv/bin/python fetch_bluesky.py
