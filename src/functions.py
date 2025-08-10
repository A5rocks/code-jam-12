"""The main script file for Pyodide."""

from js import document
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch

from parser import tokenize


def parse_input(*args) -> None:
    """Start of the parser."""
    print("testing")
    y = tokenize(document.getElementById("query-input").value)
    print(y[-2].text)  # TODO: Put SQL Parser in
    return y


async def get_user_data(user: dict) -> dict:
    """Pyfetch command example."""
    url = f"https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor={user[-2].text}"
    response = await pyfetch(url)
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
<td colspan="4" style="text-align: left; overflow-wrap: anywhere; word-wrap: break-word; padding: 20px; color: #666">
            {data_point["record"]["text"].replace("\n", "<br>")}
</td>
</tr>"""
        except KeyError:
            continue  # Handle if a field is missing (no text maybe?)
    return val

proxy_f = create_proxy(parse_input)
document.getElementById("execute-btn").addEventListener("click", proxy_f)
