from typing import List, Protocol

from src.server.hot_key.entity.hot_key_option import HotKeyOption
from src.server.hot_key.repository.hot_key_repository import (
    HotKeyRepository,
    HotKeyTuple,
)


class HotKeyService(Protocol):

    def list_hot_keys(self) -> List[HotKeyOption]: ...

    def get_default_hot_key(self) -> HotKeyOption | None: ...


class HotKeyServiceImpl(HotKeyService):

    def __init__(self, repository: HotKeyRepository):
        self._repository = repository

    def list_hot_keys(self) -> List[HotKeyOption]:
        return [
            self._to_entity(entry)
            for entry in self._repository.read_available_hot_keys()
        ]

    def get_default_hot_key(self) -> HotKeyOption | None:
        for entry in self._repository.read_available_hot_keys():
            if entry[2]:
                return self._to_entity(entry)
        return None

    def _to_entity(self, entry: HotKeyTuple) -> HotKeyOption:
        return HotKeyOption(name=entry[0], display_name=entry[1], is_default=entry[2])
