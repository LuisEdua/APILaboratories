from abc import ABC, abstractmethod
from typing import Any


class IUserService(ABC):

    @abstractmethod
    def validate(self, request) -> Any:
        pass

    @abstractmethod
    def create(self, request) -> Any:
        pass

    @abstractmethod
    def update(self, request) -> Any:
        pass

    @abstractmethod
    def delete(self, request) -> Any:
        pass


class IDispositiveService(ABC):

    @abstractmethod
    def list(self, id) -> Any:
        pass

    @abstractmethod
    def create(self, request) -> Any:
        pass

    @abstractmethod
    def update(self, request) -> Any:
        pass

    @abstractmethod
    def delete(self, id) -> Any:
        pass

    @abstractmethod
    def find_by_id(self, id) -> Any:
        pass

    @abstractmethod
    def find_by_serial_number(self, serial_number) -> Any:
        pass


class ISessionService(ABC):

    @abstractmethod
    def validate(self, request) -> Any:
        pass


class IMeasuresService(ABC):

    @abstractmethod
    def list(self, esp32_id) -> Any:
        pass

    @abstractmethod
    def create(self, request) -> Any:
        pass
