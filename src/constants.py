from enum import Enum


class ExceptionRangeType(Enum):
    MON = "mon"
    VACATION = "vacation"


class ExceptionDayType(Enum):
    EXCEPTION = "exception"
    HOLIDAY = "holiday"
