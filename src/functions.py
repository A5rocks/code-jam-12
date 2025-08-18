"""The main script file for Pyodide."""

from js import Event, document, window
from pyodide.ffi import create_proxy
from pyodide.ffi.wrappers import set_timeout

import frontend
from frontend import CLEAR_BUTTON, EXECUTE_BUTTON, clear_interface, update_table
from parser import ParentKind, Token, TokenKind, Tree, parse, tokenize


def flatten_response(data: dict) -> dict:
    """Flatten a dictionary."""
    flattened_result = {}

    def _flatten(current: dict, name: str = "") -> dict:
        if isinstance(current, dict):
            for field, value in current.items():
                _flatten(value, name + field + "_")
        elif isinstance(current, list):
            """old code
            # for idx, i in enumerate(current):
            #     _flatten(i, name + str(idx) + "_")
            """
        else:
            flattened_result[name[:-1].lower()] = current  # Drops the extra _

    _flatten(data)
    return flattened_result


def blue_screen_of_death() -> None:
    """Easter Egg: Show WinXP Blue Screen of Death."""
    input_field = document.getElementById("query-input")
    if input_field:
        input_field.value = ""

    bsod = document.createElement("div")
    bsod.className = "bsod-overlay"
    bsod.innerHTML = (
        '<div class="bsod-content">'
        '  <div class="bsod-header">A problem has been detected and Windows has been shut down to prevent damage '
        "  to your computer.</div>"
        '  <div class="bsod-error">IRQL_NOT_LESS_OR_EQUAL</div>'
        '  <div class="bsod-text">'
        "    If this is the first time you've seen this stop error screen, "
        "    restart your computer. If this screen appears again, follow these steps:<br><br>"
        "    Check to make sure any new hardware or software is properly installed. "
        "    If this is a new installation, ask your hardware or software manufacturer "
        "    for any Windows updates you might need.<br><br>"
        "    If problems continue, disable or remove any newly installed hardware or software. "
        "    Disable BIOS memory options such as caching or shadowing. If you need to use "
        "    Safe Mode to remove or disable components, restart your computer, press F8 "
        "    to select Advanced Startup Options, and then select Safe Mode."
        "  </div>"
        '  <div class="bsod-technical">'
        "    Technical information:<br><br>"
        "    *** STOP: 0x0000000A (0xFE520004, 0x00000001, 0x00000001, 0x804F9319)<br><br>"
        "    *** Address 804F9319 base at 804D7000, DateStamp 3844d96e - ntoskrnl.exe<br><br>"
        "    Beginning dump of physical memory<br>"
        "    Physical memory dump complete.<br>"
        "    Contact your system administrator or technical support group for further assistance."
        "  </div>"
        "</div>"
    )

    document.body.appendChild(bsod)
    frontend.flash_screen("#0000ff", 100)

    def remove_bsod() -> None:
        if bsod.parentNode:
            document.body.removeChild(bsod)
        frontend.update_status("System recovered from critical error", "warning")
        frontend.trigger_electric_wave()

    set_timeout(create_proxy(remove_bsod), 4000)


def clean_value(text: str) -> str:
    """Remove surrounding single/double quotes if present."""
    if isinstance(text, str) and (text[0] == text[-1]) and text[0] in ("'", '"'):
        return text[1:-1]
    return text


def get_text(node: Tree) -> str:
    """Recursively get the string value from a node (Parent or Token)."""
    if hasattr(node, "text"):
        return node.text
    if hasattr(node, "children"):
        return " ".join(get_text(child) for child in node.children)
    return str(node)


def walk_where(node: Tree) -> list[tuple | str]:
    """Flatten sql expressions into [tuple, 'AND', tuple, ...]."""
    if getattr(node, "kind", None).name == "EXPR_BINARY":
        left, op, right = node.children
        op_text = getattr(op, "text", None)

        if op_text in ("AND", "OR"):
            return [*walk_where(left), op_text, *walk_where(right)]

        return [(clean_value(get_text(left)), op_text, clean_value(get_text(right)))]

    if hasattr(node, "children"):
        result = []
        for child in node.children:
            result.extend(walk_where(child))
        return result

    return []


def extract_where(tree: Tree) -> tuple[str, str] | None:
    """Extract the where clause from the tree."""
    if not tree.kind == ParentKind.FILE:
        raise ValueError
    stmt = tree.children[0]
    for c in stmt.children:
        if c.kind == ParentKind.WHERE_CLAUSE:
            return walk_where(c.children[1])
    return []


def extract_fields(tree: Tree) -> list[Token] | None:
    """Extract the fields from the tree."""
    if not tree.kind == ParentKind.FILE:
        raise ValueError
    stmt = tree.children[0]
    for c in stmt.children:
        if c.kind == ParentKind.FIELD_LIST:
            return c.children[::2]
    return []


def extract_table(tree: Tree) -> str:
    """Extract the Table from the tree."""
    if tree.kind != ParentKind.FILE:
        raise ValueError

    stmt = tree.children[0]  # SELECT_STMT
    for c in stmt.children:
        if c.kind == ParentKind.FROM_CLAUSE:
            for child in c.children:
                if child.kind == TokenKind.IDENTIFIER:
                    return child.text
            break
    return ""


async def parse_input(_: Event) -> None:
    """Start of the parser."""
    query = document.getElementById("query-input").value.strip()

    if not query:
        frontend.update_status("Enter a SQL query to execute", "warning")
        return

    clean_query = query.upper().replace(";", "").replace(",", "").strip()
    if "DROP TABLE USERS" in clean_query:
        blue_screen_of_death()
        return

    tree: Tree = parse(tokenize(query))
    await sql_to_api_handler(tree)


async def processor(api: tuple[str, str], table: str) -> dict:  # noqa: PLR0912 C901 PLR0915
    """Process the sql statements into a api call."""
    val = {}
    if table == "feed":
        if api[0] == "actor":
            feed = await window.session.get_actor_feeds(api[2])
            val = feed["feeds"]
        elif api[0] == "author":
            feed = await window.session.get_author_feed(api[2])
            val = feed["feed"]
    elif table == "timeline":
        feed = await window.session.get_timeline()
        val = feed["feed"]
    elif table == "profile":
        if api[0] == "actors":
            feed = await window.session.get_profile(api[2])
            val = feed
        else:
            feed = await window.session.get_profile(None)
            if isinstance(feed, dict) and feed.get("stealth_error"):
                return "stealth_error"
            val = feed
    elif table == "suggestions":
        if api[0] == "actors":
            feed = await window.session.get_suggestions(api[2])
            val = feed["actors"]
        else:
            feed = await window.session.get_suggested_feeds()
            val = feed["feeds"]
    elif table == "likes":
        if api[0] == "actor":
            feed = await window.session.get_actor_likes(api[2])
            val = feed["feeds"]
        else:
            pass
    elif table == "followers":
        if api[0] == "actor":
            feed = await window.session.get_followers(api[2])
            val = feed["followers"]
        else:
            pass
    elif table == "following":
        if api[0] == "actor":
            feed = await window.session.get_following(api[2])
            val = feed["followers"]
        else:
            pass
    elif table == "mutuals":
        if api[0] == "actor":
            feed = await window.session.get_mutual_followers(api[2])
            val = feed["followers"]
        else:
            pass
    elif table == "tables":
        val = [
            {"Table_Name": _}
            for _ in [
                "feed",
                "timeline",
                "profile",
                "suggestions",
                "suggested_feed",
                "likes",
                "followers",
                "following",
                "mutuals",
            ]
        ]
    return val


def _extract_images_from_post(data: dict) -> str:
    """Extract any embedded images from a post and return them as a delimited string."""
    if not isinstance(data, dict):
        return ""

    if "post" not in data:
        return ""

    post = data["post"]

    # Check if the post has embedded content
    if "embed" not in post:
        return ""

    embed_type = post["embed"].get("$type", "")

    # Only process image embeds
    if embed_type != "app.bsky.embed.images#view":
        return ""

    images = post["embed"].get("images", [])
    if not images:
        return ""

    image_links = []
    for image in images:
        image_link = f"{image['thumb']},{image['fullsize']},{image['alt']}"
        image_links.append(image_link)

    return " | ".join(image_links)


async def sql_to_api_handler(tokens: Tree) -> dict:
    """Handle going from SQL to the API."""
    where_expr = extract_where(tokens)
    table = extract_table(tokens)
    fields = extract_fields(tokens)
    field_tokens = [i.children[0] for i in fields if i.kind != TokenKind.STAR]

    for i in where_expr:
        if i[0] in ["actor", "author", "feed"]:
            api = i
            break
    else:
        # No Where Expression Matches
        api = ["", ""]

    val = await processor(api, table)
    if not val:
        frontend.clear_interface("")
        frontend.update_status(f"Error getting from {table}", "error")
        frontend.trigger_electric_wave()
        return {}

    # Handle stealth mode error for profile queries
    if val == "stealth_error":
        frontend.clear_interface("")
        frontend.update_status(
            "Cannot get own profile in stealth mode. Try: SELECT * FROM profile WHERE actors = 'username.bsky.social'",
            "warning",
        )
        frontend.trigger_electric_wave()
        return {}

    if isinstance(val, dict):
        val = [val]

    tb = document.getElementById("table-body")
    tb.innerHTML = ""
    head = []
    if field_tokens:
        head = [j.text for j in field_tokens]
    body = []

    for i in val:
        data = i

        # Only try to extract images if the data structure supports it
        images = _extract_images_from_post(data)
        if images and "post" in data:
            data["post"]["images"] = images

        d = flatten_response(data)

        if field_tokens:
            body.append({j: d.get(j.lower(), "") for j in head})
        else:
            body.append(d)
            [head.append(k) for k in d if k not in head]

    update_table(head, body)
    frontend.update_status(f"Data successfully retrieved from {table}", "success")
    return val


EXECUTE_BUTTON.addEventListener("click", create_proxy(parse_input))
CLEAR_BUTTON.addEventListener("click", create_proxy(clear_interface))
