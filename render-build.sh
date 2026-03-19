#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Install Playwright browsers (CORRECT WAY for Render)
python -m playwright install --with-deps chromium