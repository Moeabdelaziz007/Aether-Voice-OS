"""Pytest configuration to avoid TCC sandbox issues."""

import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

collect_ignore_glob = [".*", "*.env*", "apps/*", "node_modules/*", "cortex/*"]
