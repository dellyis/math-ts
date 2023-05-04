from typing import List, Set, Tuple, Union

from pytils import numeral


def format_time(time: int) -> str:
    days, time = divmod(time, 86400)
    hours, time = divmod(time, 3600)
    minutes, seconds = divmod(time, 60)
    formatted_time = []
    if days:
        formatted_time.append(numeral.get_plural(days, "день, дня, дней"))
    if hours:
        formatted_time.append(numeral.get_plural(hours, "час, часа, часов"))
    if minutes:
        formatted_time.append(numeral.get_plural(minutes, "минута, минуты, минут"))
    if seconds:
        formatted_time.append(numeral.get_plural(seconds, "секунда, секунды, секунд"))
    return " ".join(formatted_time)


def format_range(array: Union[List, Set, Tuple]) -> str:
    ranges = []

    for i in sorted(set(array)):
        if not ranges or i > ranges[-1][-1] + 1:
            ranges.append([i])
        else:
            ranges[-1].append(i)

    return ", ".join(f"{r[0]}-{r[-1]}" if len(r) > 1 else str(r[0]) for r in ranges)
