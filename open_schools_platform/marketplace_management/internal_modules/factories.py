from open_schools_platform.marketplace_management.internal_modules.module_manager import (
    ModuleManager,
)
from open_schools_platform.marketplace_management.internal_modules.module_registry import (
    ModuleRegistry,
)


def make_module_manager() -> ModuleManager:
    module_registry = ModuleRegistry()
    return ModuleManager(module_registry)
