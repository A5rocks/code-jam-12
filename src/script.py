import re

from pyodide.http import pyfetch
from js import document


c = re.compile(r"(?i)SELECT (?P<fields>.+) FROM (?P<table>.+) WHERE actor=(?P<did>did:plc:(.{24})|(?P<user>.+))")


def do_something(name: str) -> None:
    """Nothing, just plaiting with functions."""
    print(f"Hello {name}")


def parse_input(sql_data: str) -> None:
    """Start of the parser."""
    data = c.match(sql_data)
    return data


async def get_user_data(user: dict) -> dict:
    """Pyfetch command example."""
    response = await pyfetch(f"https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor={user['user']}")
    val = (await response.json())["feed"]
    tb = document.getElementById("table-body")
    tb.innerHTML = ""

    for i in val:
        data_point = i["post"]
        try:
            tb.innerHTML += f"""<tr>
            <td colspan="2" style="text-align: center; padding: 20px; color: #666">
                        {data_point["author"]["displayName"]}
            </td>
            <td colspan="4" style="text-align: center; padding: 20px; color: #666">
                        {data_point["record"]["text"]}
            </td>
            </tr>"""
        except:
            continue
    return val
