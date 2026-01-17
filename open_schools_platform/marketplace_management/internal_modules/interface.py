from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass
class ModuleInitResultDTO:
    success: bool


class InternalModule(ABC):
    @abstractmethod
    def get_app_id(self) -> UUID:
        pass

    @abstractmethod
    def init(self, **kwargs) -> ModuleInitResultDTO:
        pass

    @abstractmethod
    def disable(self):
        pass

    @abstractmethod
    def uninstall(self):
        pass
