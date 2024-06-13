import asyncio

import pytest
import pytest_asyncio
from aiogram.fsm.storage.memory import MemoryStorage


class InClass:
    id = 1
class MockMess:
    from_user = InClass



# class StateTest:
#     def __init__(self) -> None:
#         self.state = None
#
#     async def clear(self) -> None:
#         self.state = None
#
#     async def get_state(self):
#         return self.state
#
#     async def set_state(self):
#         return self.state

    # async def set_state(self, key: StorageKey, state: StateType = None) -> None:
    #     self.storage[key].state = state.state if isinstance(state, State) else state

# @pytest_asyncio.fixture(scope="session")
# async def storage():
#     tmp_storage = MemoryStorage()
#     try:
#         yield tmp_storage
#     finally:
#         await tmp_storage.close()
#
#
# @pytest_asyncio.fixture(scope="session")
# async def event_loop():
#     return asyncio.get_event_loop()
