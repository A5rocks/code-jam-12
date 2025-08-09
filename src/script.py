import re

from pyodide.http import pyfetch

c = re.compile(r"(?i)SELECT (?P<fields>.+) FROM (?P<table>.+) WHERE actor=(?P<did>did:plc:(.{24})|(?P<user>.+))")


def do_something(name: str) -> None:
    """Nothing, just plaiting with functions."""
    print(f"Hello {name}")


def parse_input(sql_data: str) -> None:
    """Start of the parser."""
    data = c.match(sql_data)
    print(data)
    return data


async def get_user_data(user: dict) -> dict:
    """Pyfetch command example."""
    print(user)
    response = await pyfetch(f"https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor={user['user']}")
    val = await response.json()
    print(val)
    return val
