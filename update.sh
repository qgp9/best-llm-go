#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ -x "/usr/bin/python3" ]; then
    PYTHON_BIN="/usr/bin/python3"
else
    PYTHON_BIN="python3"
fi

echo "🔄 Updating OpenCode Go models & Artificial Analysis benchmarks..."
# Pinned AA snapshot (v4-era, 2026-10-27): AA is mid-migration to Intelligence
# Index v5.0 and un-remeasured models vanish from the feed. Keep frozen until
# the v5.0 rollout completes; unset to resume daily benchmark updates.
export FREEZE_AA=1
$PYTHON_BIN update_data.py
echo "🔄 Updating OpenCode console provider catalog (limits, modalities, pricing)..."
$PYTHON_BIN build_console_catalog.py
echo "🔄 Updating Free Models catalog for OpenCode, OpenRouter & CommandCode..."
$PYTHON_BIN build_free_catalog.py
echo "🔄 Updating Decision Models catalog (OpenRouter Decisions API)..."
$PYTHON_BIN build_decision_catalog.py
echo "🔄 Updating News feed (HN: Go/Zen + providers)..."
$PYTHON_BIN build_news.py
echo "✅ Update complete! Refresh index.html, free_models.html or decisions.html in your browser to see the latest data."
