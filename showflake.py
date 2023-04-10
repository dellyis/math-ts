from time import time


class SnowflakeGenerator:
    EPOCH: int = 1672531200000

    def __init__(self):
        self._process: int = int(time() * 1000)
        self._process_ticks: int = 0

    def generate(self) -> int:
        new_process = int(time() * 1000)

        if new_process == self._process:
            self._process_ticks += 1
            return ((new_process - self.EPOCH) << 22) | self._process_ticks

        self._process = new_process
        self._process_ticks = 0
        return ((new_process - self.EPOCH) << 22) | self._process_ticks
