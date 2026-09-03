#!/usr/bin/env python3
"""Run the positive fixture's real public-contract behavior checks."""

from __future__ import annotations

import unittest
from pathlib import Path


project_root = Path(__file__).resolve().parent
suite = unittest.defaultTestLoader.discover(str(project_root / "test"))
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
