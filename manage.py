#!/usr/bin/env python
"""Compatibility shim for the backend Django command entry."""
from pathlib import Path

from backend.manage_entry import main


if __name__ == '__main__':
    main(project_root=Path(__file__).resolve().parent)
