from js import Element, Math, document
from pyodide.ffi import create_proxy
from pyodide.ffi.wrappers import set_interval, set_timeout

QUERY_INPUT = document.getElementById("query-input")
EXECUTE_BUTTON = document.getElementById("execute-btn")
CANCEL_BUTTON = document.getElementById("cancel-btn")
CLEAR_BUTTON = document.getElementById("clear-btn")
TABLE_HEAD = document.getElementById("table-head")
TABLE_BODY = document.getElementById("table-body")
STATUS_MESSAGE = document.getElementById("status-message")
CONNECTION_INFO = document.getElementById("connection-info")
LOADING_OVERLAY = document.getElementById("loading-overlay")
ELECTRIC_WAVE = document.getElementById("electric-wave")


def electric_wave_trigger() -> None:
    """Roll to see if you will activate the electric wave."""
    if Math.random() < 0.03:
        ELECTRIC_WAVE.classList.remove("active")

        def _activate() -> None:
            ELECTRIC_WAVE.classList.add("active")

        set_timeout(create_proxy(_activate), 10)


def update_status(message: str, stat_type: str = "info") -> None:
    """Update the status with a given message."""
    STATUS_MESSAGE.textContent = message
    STATUS_MESSAGE.className = f"status-{stat_type}"

    # blink effect for errors
    if stat_type == "error":
        STATUS_MESSAGE.style.animation = "blink 0.5s 3"

        def _deactivate() -> Element:
            STATUS_MESSAGE.style.animation = ""

        set_timeout(_deactivate, 1500)


def clear_query_input() -> None:
    """Clear the Query field."""
    QUERY_INPUT.style.opacity = "0.3"

    def _clear() -> None:
        QUERY_INPUT.value = ""
        QUERY_INPUT.style.transition = "opacity 0.3s ease"
        QUERY_INPUT.style.opacity = "1"

    set_timeout(_clear, 150)


def show_empty_table() -> None:
    """Empty the table."""
    empty_row = document.createElement("tr")
    empty_cell = document.createElement("td")
    empty_cell.textContent = "no data found"
    empty_cell.colSpan = 8
    empty_cell.style.textAlign = "center"
    empty_cell.style.padding = "40px 20px"
    empty_cell.style.color = "#666"
    empty_cell.style.fontStyle = "italic"
    empty_row.appendChild(empty_cell)
    TABLE_BODY.replaceChildren(empty_row)

    TABLE_HEAD.style.opacity = "1"
    TABLE_BODY.style.opacity = "1"
    update_connection_info(0, "no results")


def update_connection_info(row: int, status: str) -> None:
    """Update the connection info."""
    CONNECTION_INFO.textContent = f"rows: {row} | status: {status}"


def clear_interface(*args) -> None:
    """Clear the user interface."""
    clear_query_input()
    show_empty_table()
    update_status("interface cleared", "info")
    update_connection_info(0, "waiting")


set_interval(create_proxy(electric_wave_trigger), 1000)
