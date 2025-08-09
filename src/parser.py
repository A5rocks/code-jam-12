from __future__ import annotations

import string
from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class Token:
    """A token produced by tokenization."""

    kind: TokenKind
    text: str
    start_pos: int
    end_pos: int


class TokenKind(Enum):
    """What the token represents."""

    # keywords
    SELECT = auto()
    FROM = auto()

    # literals
    STRING = auto()
    IDENTIFIER = auto()

    # structure
    COMMA = auto()
    STAR = auto()
    EOF = auto()
    ERROR = auto()


KEYWORDS = {
    "SELECT": TokenKind.SELECT,
    "FROM": TokenKind.FROM,
}


@dataclass
class Cursor:
    """Helper class to allow peeking into a stream of characters."""

    contents: str
    index: int = 0

    def peek(self) -> str:
        """Look one character ahead in the stream."""
        return self.contents[self.index : self.index + 1]

    def next(self) -> str:
        """Get the next character in the stream."""
        c = self.peek()
        if c != "":
            self.index += 1
        return c


def tokenize(query: string) -> list[Token]:
    """Turn a query into a list of tokens."""
    result = []

    cursor = Cursor(query)
    while True:
        idx = cursor.index
        char = cursor.next()

        if char == "":
            result.append(Token(TokenKind.EOF, "", idx, idx))
            break

        if char in string.ascii_letters:
            char = cursor.peek()

            while char in string.ascii_letters + ".":
                cursor.next()
                char = cursor.peek()
                if char == "":
                    break

            identifier = cursor.contents[idx : cursor.index]
            kind = KEYWORDS.get(identifier, TokenKind.IDENTIFIER)
            result.append(Token(kind, identifier, idx, cursor.index))

        elif char == ",":
            result.append(Token(TokenKind.COMMA, ",", idx, cursor.index))

        elif char == "*":
            result.append(Token(TokenKind.STAR, ",", idx, cursor.index))

        elif char == "'":
            # idk escaping rules in SQL lol
            char = cursor.peek()
            while char != "'":
                cursor.next()
                char = cursor.peek()
                if char == "":
                    break

            cursor.next()  # get the last '

            string_result = cursor.contents[idx : cursor.index + 1]
            print(string_result)
            kind = TokenKind.STRING if string_result.endswith("'") and len(string_result) > 1 else TokenKind.ERROR
            result.append(Token(kind, string_result, idx, cursor.index + 1))

    return result


def check_tok(before: str, after: TokenKind) -> None:
    """Test helper which checks a string tokenizes to a single given token kind."""
    assert [tok.kind for tok in tokenize(before)] == [after, TokenKind.EOF]


def stringify_tokens(query: str) -> str:
    """Test helper which turns a query into a repr of the tokens.

    Used for manual snapshot testing.
    """
    tokens = tokenize(query)
    result = ""
    for i, c in enumerate(query):
        for tok in tokens:
            if tok.start_pos == i:
                result += ">"

        for tok in tokens:
            if tok.end_pos == i:
                result += "<"

        result += c

    i += 1
    for tok in tokens[:-1]:  # don't print EOF
        if tok.end_pos == i:
            result += "<"

    return result


def test_simple_tokens() -> None:
    """Tests that various things tokenize correct in minimal cases."""
    assert [tok.kind for tok in tokenize("")] == [TokenKind.EOF]
    check_tok("SELECT", TokenKind.SELECT)
    check_tok("FROM", TokenKind.FROM)
    check_tok("'hello :)'", TokenKind.STRING)
    check_tok(",", TokenKind.COMMA)
    check_tok("*", TokenKind.STAR)
    check_tok("username", TokenKind.IDENTIFIER)


def test_tokenize_simple_select() -> None:
    """Tests that tokenization works in more general cases."""
    assert stringify_tokens("SELECT * FROM posts") == ">SELECT< >*< >FROM< >posts<"


if __name__ == "__main__":
    query = input("query> ")
    print(stringify_tokens(query))
    from pprint import pprint

    print()
    pprint(tokenize(query))
