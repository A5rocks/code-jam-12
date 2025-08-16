from typing import Literal

from js import Element, Event, Math, document
from pyodide.ffi import create_proxy
from pyodide.ffi.wrappers import set_interval, set_timeout

# constants for random effects
ELECTRIC_WAVE_PROBABILITY = 0.03
SCREEN_FLICKER_PROBABILITY = 0.05

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
    if Math.random() < ELECTRIC_WAVE_PROBABILITY:
        ELECTRIC_WAVE.classList.remove("active")

        def _activate() -> None:
            ELECTRIC_WAVE.classList.add("active")

        set_timeout(create_proxy(_activate), 50)


def update_status(message: str, stat_type: Literal["success", "error", "warning", "info"] = "info") -> None:
    """Update the status with a given message."""
    STATUS_MESSAGE.textContent = message
    STATUS_MESSAGE.className = f"status-{stat_type}"

    # blink effect for errors
    if stat_type == "error":
        STATUS_MESSAGE.style.animation = "blink 0.5s 3"

        def _deactivate() -> None:
            STATUS_MESSAGE.style.animation = ""

        set_timeout(create_proxy(_deactivate), 1500)


def clear_query_input() -> None:
    """Clear the Query field."""
    QUERY_INPUT.style.opacity = "0.3"

    def _clear() -> None:
        QUERY_INPUT.value = ""
        QUERY_INPUT.style.transition = "opacity 0.3s ease"
        QUERY_INPUT.style.opacity = "1"

    set_timeout(create_proxy(_clear), 150)


def show_empty_table() -> int:
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

    TABLE_HEAD.innerHTML = "<tr><td>No Columns</td></tr>"
    print(TABLE_HEAD)
    TABLE_BODY.replaceChildren(empty_row)

    TABLE_HEAD.style.opacity = "1"
    TABLE_BODY.style.opacity = "1"
    update_connection_info(0, "no results")
    return 1


def update_connection_info(row: int, status: str) -> None:
    """Update the connection info."""
    CONNECTION_INFO.textContent = f"rows: {row} | status: {status}"


def clear_interface(_: Event) -> None:
    """Clear the user interface."""
    clear_query_input()
    show_empty_table()
    update_status("interface cleared", "info")
    update_connection_info(0, "waiting")


def show_loading(*, show: bool = True) -> None:
    """Show/hide loading overlay with spinner."""
    if show:
        LOADING_OVERLAY.classList.add("show")
        trigger_electric_wave()  # automatic effect when loading
    else:
        LOADING_OVERLAY.classList.remove("show")


def trigger_electric_wave() -> None:
    """Trigger the electric wave effect."""
    ELECTRIC_WAVE.classList.remove("active")

    def _activate() -> None:
        ELECTRIC_WAVE.classList.add("active")

    set_timeout(create_proxy(_activate), 50)


def _create_table_headers(headers: list) -> None:
    """Create table headers with staggered animation."""
    header_row = document.createElement("tr")
    for index, header in enumerate(headers):
        th = document.createElement("th")
        th.textContent = header.upper()
        th.style.opacity = "0"
        header_row.appendChild(th)

        # staggered header animation
        def _show_header(element: Element = th, delay: int = index * 50) -> None:
            def _animate() -> None:
                element.style.transition = "opacity 0.3s ease"
                element.style.opacity = "1"

            set_timeout(create_proxy(_animate), delay)

        _show_header()

    TABLE_HEAD.appendChild(header_row)


def _create_table_rows(headers: list, rows: list[dict]) -> None:
    """Create table rows with appearing effect."""
    for row_index, row_data in enumerate(rows):
        tr = document.createElement("tr")
        tr.style.opacity = "0"

        cell_values = [str(row_data.pop(header, "")) for header in headers]
        for cell_data in cell_values:
            td = document.createElement("td")
            td.textContent = str(cell_data) if cell_data else ""
            tr.appendChild(td)

        TABLE_BODY.appendChild(tr)

        # staggered row animation
        def _show_row(element: Element = tr, delay: int = (row_index * 100) + 200) -> None:
            def _animate() -> None:
                element.style.transition = "opacity 0.4s ease"
                element.style.opacity = "1"

            set_timeout(create_proxy(_animate), delay)

        _show_row()


def update_table(headers: list, rows: list[dict]) -> None:
    """Populate table with data and appearing effects."""
    # fade out effect before updating
    TABLE_HEAD.style.opacity = "0.3"
    TABLE_BODY.style.opacity = "0.3"

    def _update_content() -> None:
        # clear table
        TABLE_HEAD.innerHTML = ""
        TABLE_BODY.innerHTML = ""

        if not headers or not rows or len(rows) == 0:
            show_empty_table()
            return

        _create_table_headers(headers)
        _create_table_rows(headers, rows)

        # restore container opacity
        def _restore_opacity() -> None:
            TABLE_HEAD.style.opacity = "1"
            TABLE_BODY.style.opacity = "1"

        set_timeout(create_proxy(_restore_opacity), 300)

        # update counter
        update_connection_info(len(rows), "connected")

        # final success effect
        def _final_effect() -> None:
            trigger_electric_wave()

        set_timeout(create_proxy(_final_effect), (len(rows) * 100) + 500)

    set_timeout(create_proxy(_update_content), 200)


def set_buttons_disabled(*, disabled: bool) -> None:
    """Enable/disable buttons with visual effects."""
    EXECUTE_BUTTON.disabled = disabled
    CLEAR_BUTTON.disabled = disabled
    CANCEL_BUTTON.disabled = not disabled  # cancel only available when executing

    # visual effects on buttons
    if disabled:
        EXECUTE_BUTTON.style.opacity = "0.5"
        CLEAR_BUTTON.style.opacity = "0.5"
        CANCEL_BUTTON.style.opacity = "1"
        CANCEL_BUTTON.style.animation = "blink 1s infinite"
    else:
        EXECUTE_BUTTON.style.opacity = "1"
        CLEAR_BUTTON.style.opacity = "1"
        CANCEL_BUTTON.style.opacity = "0.7"
        CANCEL_BUTTON.style.animation = ""


def get_current_query() -> str:
    """Get current query from input."""
    return QUERY_INPUT.value.strip()


def show_input_error() -> None:
    """Error effect on input field."""
    QUERY_INPUT.style.borderColor = "#ff0000"
    QUERY_INPUT.style.boxShadow = "inset 0 0 10px rgba(255, 0, 0, 0.3)"

    def _reset() -> None:
        QUERY_INPUT.style.borderColor = "#00ff00"
        QUERY_INPUT.style.boxShadow = "inset 0 0 5px rgba(0, 255, 0, 0.3)"

    set_timeout(create_proxy(_reset), 1000)


def show_input_success() -> None:
    """Success effect on input field."""
    QUERY_INPUT.style.borderColor = "#00ff00"
    QUERY_INPUT.style.boxShadow = "inset 0 0 10px rgba(0, 255, 0, 0.5)"

    def _reset() -> None:
        QUERY_INPUT.style.boxShadow = "inset 0 0 5px rgba(0, 255, 0, 0.3)"

    set_timeout(create_proxy(_reset), 1000)


def flash_screen(color: str = "#00ff00", duration: int = 200) -> None:
    """Fullscreen flash effect for important results."""
    flash = document.createElement("div")
    flash.style.position = "fixed"
    flash.style.top = "0"
    flash.style.left = "0"
    flash.style.width = "100%"
    flash.style.height = "100%"
    flash.style.backgroundColor = color
    flash.style.opacity = "0.1"
    flash.style.pointerEvents = "none"
    flash.style.zIndex = "9999"

    document.body.appendChild(flash)

    def _fade_out() -> None:
        flash.style.transition = f"opacity {duration}ms ease"
        flash.style.opacity = "0"

        def _remove() -> None:
            document.body.removeChild(flash)

        set_timeout(create_proxy(_remove), duration)

    set_timeout(create_proxy(_fade_out), 50)


def screen_flicker_effect() -> None:
    """Occasional screen flicker (retro effect)."""
    if Math.random() < SCREEN_FLICKER_PROBABILITY:
        screen = document.querySelector(".screen")
        if screen:
            screen.style.opacity = "0.9"

            def _restore() -> None:
                screen.style.opacity = "1"

            set_timeout(create_proxy(_restore), 100)


# automatic system effects setup
set_interval(create_proxy(electric_wave_trigger), 1000)
set_interval(create_proxy(screen_flicker_effect), 5000)

# setup initial ui
update_status("system ready", "success")
update_connection_info(0, "waiting")
show_empty_table()

print("ready")
