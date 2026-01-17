from uuid import UUID

from open_schools_platform.marketplace_management.internal_modules.errors import (
    InternalModuleNotFoundError,
)
from open_schools_platform.marketplace_management.internal_modules.interface import (
    InternalModule,
)


class ModuleRegistry:
    def __init__(self):
        self.module_registry = {}

    def get_module(self, app_id: UUID) -> InternalModule:
        if app_id not in self.module_registry:
            raise InternalModuleNotFoundError()
        return self.module_registry[app_id]

    def add_module(self, app_id: UUID, module: InternalModule):
        self.module_registry[app_id] = module


module_registry = ModuleRegistry()
