import logging
import os
from typing import Dict

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fyle_xero_api.settings")
django.setup()

from apps.fyle.tasks import import_and_export_expenses

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def handle_exports(data: Dict) -> None:
    import_and_export_expenses(**data)

