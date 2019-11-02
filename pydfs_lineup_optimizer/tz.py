_TIMEZONE = 'US/Eastern'


def set_timezone(tz_name):
    # type: (str) -> None
    global _TIMEZONE
    _TIMEZONE = tz_name


def get_timezone():
    # type: () -> str
    return _TIMEZONE
