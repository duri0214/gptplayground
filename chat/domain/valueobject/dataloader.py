from abc import ABC, abstractmethod


class Dataloader(ABC):
    @property
    @abstractmethod
    def data(self):
        pass

    @abstractmethod
    def _load(self):
        pass
    
    @abstractmethod
    def _split(self, separators: list):
        pass
