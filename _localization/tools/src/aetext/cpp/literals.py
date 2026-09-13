"""Decode the finite C++ string-literal forms accepted for localization Originals."""

from __future__ import annotations


def decode_string_literal(literal: str) -> str:
    quote_index = literal.find('"')
    if quote_index < 0 or not literal.endswith('"'):
        raise ValueError("not a complete string literal")
    prefix = literal[:quote_index]
    if prefix.endswith("R"):
        delimiter_end = literal.find("(", quote_index + 1)
        delimiter = literal[quote_index + 1 : delimiter_end]
        terminator = ")" + delimiter + '"'
        if delimiter_end < 0 or not literal.endswith(terminator):
            raise ValueError("malformed raw string literal")
        return literal[delimiter_end + 1 : -len(terminator)]

    body = literal[quote_index + 1 : -1]
    result: list[str] = []
    index = 0
    simple = {
        "a": "\a",
        "b": "\b",
        "f": "\f",
        "n": "\n",
        "r": "\r",
        "t": "\t",
        "v": "\v",
        "\\": "\\",
        "'": "'",
        '"': '"',
        "?": "?",
    }
    while index < len(body):
        character = body[index]
        if character != "\\":
            result.append(character)
            index += 1
            continue
        index += 1
        if index >= len(body):
            raise ValueError("incomplete escape")
        escape = body[index]
        if escape in simple:
            result.append(simple[escape])
            index += 1
            continue
        if escape in "01234567":
            end = index + 1
            while end < min(index + 3, len(body)) and body[end] in "01234567":
                end += 1
            result.append(chr(int(body[index:end], 8)))
            index = end
            continue
        if escape == "x":
            end = index + 1
            while end < len(body) and body[end] in "0123456789abcdefABCDEF":
                end += 1
            if end == index + 1:
                raise ValueError("empty hexadecimal escape")
            result.append(chr(int(body[index + 1 : end], 16)))
            index = end
            continue
        if escape in ("u", "U"):
            digits = 4 if escape == "u" else 8
            end = index + 1 + digits
            value = body[index + 1 : end]
            if len(value) != digits or any(char not in "0123456789abcdefABCDEF" for char in value):
                raise ValueError("malformed universal character escape")
            result.append(chr(int(value, 16)))
            index = end
            continue
        if escape in "\r\n":
            if escape == "\r" and index + 1 < len(body) and body[index + 1] == "\n":
                index += 1
            index += 1
            continue
        raise ValueError(f"unsupported escape \\{escape}")
    return "".join(result)
