from datetime import date


def parse_date_flexible(date_str: str) -> date:
    """
    Accepts M/D/YYYY, M/D/YY, or M/D (assumes current year).
    Raises ValueError/IndexError on malformed or impossible dates.
    """
    parts = date_str.strip().split("/")
    month = int(parts[0])
    day = int(parts[1])
    if len(parts) == 3 and parts[2]:
        year = int(parts[2])
        if year < 100:
            year += 2000
    else:
        year = date.today().year
    return date(year, month, day)
