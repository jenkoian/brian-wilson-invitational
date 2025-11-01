#!/usr/bin/env sh

uv run duckdb -cmd "ATTACH IF NOT EXISTS 'bwi_ui.duckdb' AS bwi (READ_ONLY); CALL start_ui();"
