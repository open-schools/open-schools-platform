import importlib
import logging
import sys
from pathlib import Path
from uuid import UUID

from django.apps import AppConfig

from open_schools_platform.marketplace_management.internal_modules.module_registry import (
    module_registry,
)

logger = logging.getLogger("internal modules")


class MiniappManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "open_schools_platform.marketplace_management"

    def ready(self):
        from open_schools_platform.marketplace_management.models import App

        base_dir = Path(
            "open_schools_platform/marketplace_management/internal_modules/modules"
        )
        if str(base_dir) not in sys.path:
            sys.path.insert(0, str(base_dir))

        for item in base_dir.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                module_name = item.name
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, "module"):
                        app_id = module.module.get_app_id()
                        app = (
                            App.objects.filter(id=app_id).first()
                            if isinstance(app_id, UUID)
                            else None
                        )
                        if app is None:
                            logger.error(f"Module's app not found: {module_name}")
                        else:
                            logger.info(f"Module imported: {module_name}")
                            module_registry.add_module(app_id, module.module)
                except Exception as e:
                    logger.error(f"Error on module import {module_name}: {e}")
