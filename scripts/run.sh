#!/bin/bash
export BLUESKY_HANDLE="bluesky@daandobber.nl"
export BLUESKY_APP_PASSWORD="jfwu-tlbm-iz3q-vjei"

cd "$(dirname "$0")"
venv/bin/python fetch_bluesky.py
