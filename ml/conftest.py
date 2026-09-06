"""
conftest.py — Adds ml/src to sys.path so tests can import from src.*
without needing a package install step.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
