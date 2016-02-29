from enum import Enum


class PrimitiveType(Enum):
    """
    Enum for primitive structures.
    """

    bool = None  # auto assigned 0
    int8 = None  # auto assigned 1
    int16 = None  # ...
    int32 = None
    int64 = None
    unsigned_int8 = None
    unsigned_int16 = None
    unsigned_int32 = None
    unsigned_int64 = None
    half = None
    float = None
    double = None
    string = None
    ref = None
    type = None
