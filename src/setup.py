"""The Setup Script for pyodide."""

from pyodide.http import pyfetch


async def setup_pyodide_scripts() -> None:
    """Script to do everything for pyodide."""
    response = await pyfetch("./functions.py")
    with open("functions.py", "wb") as f:
        f.write(await response.bytes())

    # response = await pyfetch("./parser.py")
    # with open("parser.py", "wb") as f:
    #     f.write(await response.bytes())
