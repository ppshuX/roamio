"""Shared Django management entry point for root and backend shims."""
import os
import sys
from pathlib import Path


def add_project_root(project_root):
    """Ensure the repository root is importable before Django starts."""
    project_root_str = str(Path(project_root).resolve())
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)


def main(argv=None, project_root=None):
    """Run Django administrative tasks."""
    if project_root is not None:
        add_project_root(project_root)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roamio.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(argv or sys.argv)
