import logging
from uuid import UUID

from open_schools_platform.marketplace_management.internal_modules.interface import (
    InternalModule,
    ModuleInitResultDTO,
)

logger = logging.getLogger("example module")


class ExampleModule(InternalModule):
    def init(self, **kwargs) -> ModuleInitResultDTO:
        logger.error("Example module init()")
        return ModuleInitResultDTO(success=True)

    def disable(self):
        pass

    def uninstall(self):
        pass

    def get_app_id(self) -> UUID:
        return UUID("308f0508-19d7-4b6a-9178-3f9f49af183f")


module = ExampleModule()
