from collections import defaultdict
from typing import List, Optional


class TimingStatistics:

    _instance: Optional["TimingStatistics"] = None

    def __init__(self):
        self.reset()

    def reset(self):
        self._repetitions = 0
        self._results = defaultdict(list)

    @staticmethod
    def instance() -> "TimingStatistics":
        if TimingStatistics._instance is None:
            TimingStatistics._instance = TimingStatistics()
        return TimingStatistics._instance

    @property
    def repetitions(self):
        return self._repetitions

    def add_repetition(self):
        self._repetitions += 1

    def add_result(self, key: str, val: float):
        self._results[key].append(val)

    def print(self):

        for key, value in self._results.items():
            print(f"Result: {key} Value: {value}")



class StorageStatistics:

    _instance: Optional["StorageStatistics"] = None

    def __init__(self):
        self.reset()

    def reset(self):
        self._read_units = 0
        self._write_units = 0
        self._read_times: List[float] = []
        self._write_times: List[float] = []

    @staticmethod
    def instance():
        if StorageStatistics._instance is None:
            StorageStatistics._instance = StorageStatistics()
        return StorageStatistics._instance

    @property
    def read_units(self) -> int:
        return self._read_units

    def add_read_units(self, val: int):
        self._read_units += val

    @property
    def write_units(self) -> int:
        return self._write_units

    def add_write_units(self, val: int):
        self._write_units += val

    @property
    def read_times(self) -> List[float]:
        return self._read_times

    def add_read_time(self, val: float):
        self._read_times.append(val)

    @property
    def write_times(self) -> List[float]:
        return self._write_times

    def add_write_time(self, val: float):
        self._write_times.append(val)
