from enum import Enum


class PrimitiveType(Enum):
    """
    Enum for primitive structures.
    """

    bool = 0  # auto assigned 0
    int8 = 1  # auto assigned 1
    int16 = 2  # ...
    int32 = 3
    int64 = 4
    unsigned_int8 = 5
    unsigned_int16 = 6
    unsigned_int32 = 7
    unsigned_int64 = 8
    half = 9
    float = 10
    double = 11
    string = 12
    ref = 13
    type = 14
