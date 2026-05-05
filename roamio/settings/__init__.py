import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(path=None, *args, **kwargs):
        return False

# 必须在选择 prod/dev 之前加载 .env，否则 ROAMIO_SETTINGS / ROAMIO_USE_SQLITE 等永远不生效，
# Django 会直接连 MYSQL 的旧 DB_HOST。
_project_root = Path(__file__).resolve().parent.parent.parent
_dotenv_primary = _project_root / '.env'
if _dotenv_primary.exists():
    load_dotenv(_dotenv_primary)
_dotenv_override = _project_root / '.env.prod'
if _dotenv_override.exists():
    load_dotenv(_dotenv_override, override=True)

settings_name = os.getenv('ROAMIO_SETTINGS', 'dev').lower()

if settings_name in {'prod', 'production'}:
    from .prod import *  # noqa: F401,F403
elif settings_name == 'base':
    from .base import *  # noqa: F401,F403
else:
    from .dev import *  # noqa: F401,F403
