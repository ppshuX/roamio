import os

settings_name = os.getenv('ROAMIO_SETTINGS', 'dev').lower()

if settings_name in {'prod', 'production'}:
    from .prod import *  # noqa: F401,F403
elif settings_name == 'base':
    from .base import *  # noqa: F401,F403
else:
    from .dev import *  # noqa: F401,F403
