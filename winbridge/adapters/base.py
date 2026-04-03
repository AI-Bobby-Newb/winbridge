from abc import ABC, abstractmethod


class Adapter(ABC):
    @abstractmethod
    def install(self, package: str) -> None: ...

    @abstractmethod
    def remove(self, package: str) -> None: ...

    @abstractmethod
    def update(self, package: str) -> None: ...

    @abstractmethod
    def upgrade(self) -> None: ...

    @abstractmethod
    def search(self, query: str) -> list[str]: ...
