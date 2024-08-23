def update_dict(source_dict: dict, new_values: dict) -> dict:
    for k, v in new_values.items():
        source_dict[k] = v
    return source_dict


def get_between(value: int, intervals: list[tuple[int, int]]) -> tuple[int, int]:
    for i in intervals:
        if (value >= i[0]) and (value <= i[1]):
            return i

    raise ValueError('Value out of range')
