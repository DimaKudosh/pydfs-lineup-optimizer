_TIMEZONE = 'US/Eastern'


def set_timezone(tz_name: str):
    global _TIMEZONE
    _TIMEZONE = tz_name


def get_timezone() -> str:
    return _TIMEZONE
