#!/usr/bin/env bash
set -euo pipefail
streamlit run web/app.py --server.port ${PORT:-10000} --server.headless true
