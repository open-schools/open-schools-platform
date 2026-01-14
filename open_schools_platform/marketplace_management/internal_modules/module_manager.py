from uuid import UUID

from open_schools_platform.marketplace_management.internal_modules.interface import (
    InternalModule,
)
from open_schools_platform.marketplace_management.internal_modules.module_registry import (
    ModuleRegistry,
)


class ModuleManager:
    def __init__(self, module_registry: ModuleRegistry):
        self.module_registry = module_registry

    def _process_module_init_result(self, module: InternalModule):
        pass

    def initialize(
        self, app_id: str, org_id: UUID, config_data: dict | None = None
    ) -> InternalModule:
        module: InternalModule = self.module_registry.get_module(
            app_id, org_id, config_data
        )
        module_init_res = module.init()
        self._process_module_init_result(module_init_res)
        return module_init_res
