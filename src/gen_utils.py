import itertools
from pathlib import Path

import numpy as np


def update_dict(source_dict: dict, new_values: dict) -> dict:
    for k, v in new_values.items():
        source_dict[k] = v
    return source_dict


def get_between(value: int, intervals: list[tuple[int, int]]) -> tuple[int, int]:
    for i in intervals:
        if (value >= i[0]) and (value <= i[1]):
            return i

    raise ValueError('Value out of range')


def multi_pattern_rglob(pth: Path, patterns: list[str]) -> list:
    return list(itertools.chain.from_iterable(pth.rglob(pattern) for pattern in patterns))


def to_float(s: str) -> float:
    try:
        float(s)
    except ValueError:
        return -99.0


def to_int(s: str) -> int:
    try:
        int(s)
    except ValueError:
        return 0