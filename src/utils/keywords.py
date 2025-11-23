from typing import List


def unique_list(lst: List[str]) -> List[str]:
    return list(dict.fromkeys(lst))

def delete_intersections(primary: List[str], secondary: List[str]) -> List[str]:
    return [x for x in primary if x not in secondary]

def convert_to_single(lst: List[str]) -> List[str]:
    return " ".join(lst).replace("-", " ").split()

def truncate_to_even(lst: List[str]) -> List[str]:
    _lst = lst
    if len(_lst) % 2 != 0:
        _lst = _lst[:-1]
    return _lst

def convert_to_double(lst: List[str]) -> List[str]:
    _lst = truncate_to_even(lst)
    single_lst = _lst[:25]
    double_lst = []

    truncated = truncate_to_even(single_lst)
    for index in range(0, len(truncated), 2):
        double_lst.append(truncated[index] + ' ' + truncated[index + 1])

    double_lst = double_lst[:25]
    return single_lst + double_lst