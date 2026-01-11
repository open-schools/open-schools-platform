from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ModuleInitResultDTO:
    status: str

class InternalModule(ABC):
    @abstractmethod
    def init(self) -> ModuleInitResultDTO:
        pass

    @abstractmethod
    def disable(self):
        pass

    @abstractmethod
    def uninstall(self):
        pass