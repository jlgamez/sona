from typing import Protocol, Tuple

from src.server.hot_key.repository.hot_key_constants import HOT_KEY_ENTRIES

HotKeyTuple = Tuple[str, str, bool]


class HotKeyRepository(Protocol):

    def read_available_hot_keys(self) -> Tuple[HotKeyTuple, ...]: ...


class HotKeyRepositoryImpl(HotKeyRepository):

    def read_available_hot_keys(self) -> Tuple[HotKeyTuple, ...]:
        return HOT_KEY_ENTRIES
