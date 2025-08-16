"""The main script file for Pyodide."""

from js import Event, document, window
from pyodide.ffi import create_proxy

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
    y = document.getElementById("query-input").value
    tree: Tree = parse(tokenize(y))
    await sql_to_api_handler(tree)


async def processor(api: tuple[str, str], table: str) -> dict:  # noqa: PLR0912 C901
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
    return val


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
    val = processor(api, table)
    if not val:
        frontend.clear_interface("")
        frontend.update_status(f"Error getting from {table}", "error")
        frontend.trigger_electric_wave()
        return {}
    tb = document.getElementById("table-body")
    tb.innerHTML = ""
    head = []
    if field_tokens:
        head = [j.text for j in field_tokens]
    body = []
    for i in val:
        data = i

        d = flatten_response(data)
        if field_tokens:
            body.append({j: d[j.lower()] for j in head})
        else:
            body.append(d)
            [head.append(k) for k in d if k not in head]

    update_table(head, body)
    frontend.update_status(f"Data successfully retrieved from {table}", "success")
    return val


EXECUTE_BUTTON.addEventListener("click", create_proxy(parse_input))
CLEAR_BUTTON.addEventListener("click", create_proxy(clear_interface))
