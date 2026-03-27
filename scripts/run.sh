#!/bin/bash
export BLUESKY_HANDLE="lid@voorbeeld.nl"
export BLUESKY_APP_PASSWORD="***VERWIJDERD***"

cd "$(dirname "$0")"
venv/bin/python fetch_bluesky.py
