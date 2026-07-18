def format_duration(minutes):
    if not minutes or minutes < 1:
        return "0m"
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def split_duration(minutes):
    if not minutes or minutes < 1:
        return (0, 0)
    return (minutes // 60, minutes % 60)
