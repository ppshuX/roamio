#!/usr/bin/env python
"""Django command-line entry point for the backend workspace."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_STR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_STR)

from backend.manage_entry import main


if __name__ == '__main__':
    main(project_root=PROJECT_ROOT)
