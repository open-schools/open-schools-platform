from open_schools_platform.marketplace_management.internal_modules.module_manager import (
    ModuleManager,
)
from open_schools_platform.marketplace_management.internal_modules.module_registry import (
    module_registry,
)


def make_module_manager() -> ModuleManager:
    return ModuleManager(module_registry)
