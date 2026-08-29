"""Production Tree-sitter implementation of the bounded AeText C/C++ source scanner."""

from __future__ import annotations

from bisect import bisect_right
from collections.abc import Iterable, Iterator
from pathlib import Path

import tree_sitter_cpp
from tree_sitter import Language, Node, Parser

from .core.scanner_contract import (
    ROLE_ORDER,
    WRAPPERS,
    MacroDefinition,
    diagnostic,
    relative_path,
)
from .cpp.literals import decode_string_literal

_CPP_LANGUAGE = Language(tree_sitter_cpp.language())
_PREPROC_BRANCHES = {
    "preproc_if",
    "preproc_ifdef",
    "preproc_ifndef",
    "preproc_elif",
    "preproc_else",
}


def _walk(node: Node) -> Iterator[Node]:
    yield node
    for child in node.named_children:
        yield from _walk(child)


def _node_bytes(node: Node, source: bytes) -> bytes:
    return source[node.start_byte : node.end_byte]


def _node_text(node: Node, source: bytes) -> str:
    return _node_bytes(node, source).decode("utf-8")


def _line_starts(source: bytes) -> list[int]:
    return [0, *(index + 1 for index, value in enumerate(source) if value == 0x0A)]


def _position(source: bytes, starts: list[int], offset: int) -> tuple[int, int]:
    line_index = bisect_right(starts, offset) - 1
    prefix = source[starts[line_index] : offset].decode("utf-8")
    return line_index + 1, len(prefix) + 1


def _location(node: Node, source: bytes, starts: list[int], path: str) -> dict[str, object]:
    line, column = _position(source, starts, node.start_byte)
    return {"path": path, "line": line, "column": column}


def _function_name(node: Node, source: bytes) -> str | None:
    current = node.parent
    while current is not None and current.type != "function_definition":
        current = current.parent
    if current is None:
        return None
    declarator = current.child_by_field_name("declarator")
    while declarator is not None:
        if declarator.type in {"identifier", "field_identifier"}:
            return _node_text(declarator, source)
        if declarator.type in {"qualified_identifier", "scoped_identifier"}:
            name = declarator.child_by_field_name("name")
            return None if name is None else _node_text(name, source)
        nested = declarator.child_by_field_name("declarator")
        if nested is None:
            nested = next(
                (
                    child
                    for child in declarator.named_children
                    if child.type
                    in {
                        "function_declarator",
                        "identifier",
                        "field_identifier",
                        "qualified_identifier",
                        "scoped_identifier",
                    }
                ),
                None,
            )
        declarator = nested
    return None


def _is_zero_expression(value: str) -> bool:
    expression = value.strip()
    while expression.startswith("(") and expression.endswith(")"):
        expression = expression[1:-1].strip()
    return expression == "0"


def _contains(container: Node, candidate: Node) -> bool:
    return container.start_byte <= candidate.start_byte and candidate.end_byte <= container.end_byte


def _disabled_by_literal_zero(node: Node, source: bytes) -> bool:
    current = node.parent
    while current is not None:
        if current.type in {"preproc_if", "preproc_elif"}:
            condition = current.child_by_field_name("condition")
            if condition is not None and _is_zero_expression(_node_text(condition, source)):
                alternative = current.child_by_field_name("alternative")
                if alternative is None or not _contains(alternative, node):
                    return True
        current = current.parent
    return False


def _inside_preprocessor_header(node: Node) -> bool:
    current = node.parent
    while current is not None:
        if current.type.startswith("preproc_"):
            if current.type not in _PREPROC_BRANCHES:
                return True
            condition = current.child_by_field_name("condition")
            if condition is not None and _contains(condition, node):
                return True
        current = current.parent
    return False


def _value_node(root: Node) -> Node | None:
    for node in _walk(root):
        if node.type == "init_declarator":
            return node.child_by_field_name("value")
    return None


def _string_nodes(value: Node) -> list[Node] | None:
    if value.type in {"string_literal", "raw_string_literal"}:
        return [value]
    if value.type == "concatenated_string":
        children = [
            child
            for child in value.named_children
            if child.type in {"string_literal", "raw_string_literal"}
        ]
        return children if len(children) == len(value.named_children) else None
    return None


def _parse_macro_original(value: Node, source: bytes) -> str:
    body = _node_bytes(value, source)
    synthetic = b"auto aetext_value = " + body + b";\n"
    tree = Parser(_CPP_LANGUAGE).parse(synthetic)
    parsed_value = _value_node(tree.root_node)
    if parsed_value is None or parsed_value.has_error:
        raise ValueError("macro value is not a complete C++ expression")
    literals = _string_nodes(parsed_value)
    if not literals:
        raise TypeError("localization macro must contain only string literals")
    return "".join(decode_string_literal(_node_text(literal, synthetic)) for literal in literals)


def _scan_macros(
    root: Node,
    source: bytes,
    starts: list[int],
    path: str,
    diagnostics: list[dict[str, object]],
) -> list[MacroDefinition]:
    macros: list[MacroDefinition] = []
    for node in _walk(root):
        if node.type not in {"preproc_def", "preproc_function_def"}:
            continue
        if _disabled_by_literal_zero(node, source):
            continue
        name = node.child_by_field_name("name")
        if name is None:
            continue
        stable_id = _node_text(name, source)
        if not stable_id.startswith("L10N_"):
            continue
        location = _location(name, source, starts, path)
        if node.type == "preproc_function_def":
            diagnostics.append(
                diagnostic(
                    "AET1007",
                    f"localization macro must be object-like: {stable_id}",
                    path,
                    int(location["line"]),
                    int(location["column"]),
                )
            )
            continue
        value = node.child_by_field_name("value")
        if value is None:
            diagnostics.append(
                diagnostic(
                    "AET1008",
                    f"localization macro must contain only string literals: {stable_id}",
                    path,
                    int(location["line"]),
                    int(location["column"]),
                )
            )
            continue
        try:
            original = _parse_macro_original(value, source)
        except TypeError:
            diagnostics.append(
                diagnostic(
                    "AET1008",
                    f"localization macro must contain only string literals: {stable_id}",
                    path,
                    int(location["line"]),
                    int(location["column"]),
                )
            )
            continue
        except (UnicodeError, ValueError, OverflowError) as error:
            diagnostics.append(
                diagnostic(
                    "AET1009",
                    f"invalid localization string literal {stable_id}: {error}",
                    path,
                    int(location["line"]),
                    int(location["column"]),
                )
            )
            continue
        macros.append(MacroDefinition(stable_id, original, location))
    return macros


def _scan_calls(
    root: Node,
    source: bytes,
    starts: list[int],
    path: str,
    input_ordinal: int,
    diagnostics: list[dict[str, object]],
) -> list[dict[str, object]]:
    calls: list[dict[str, object]] = []
    identifiers = sorted(
        (node for node in _walk(root) if node.type == "identifier"),
        key=lambda node: node.start_byte,
    )
    for node in identifiers:
        wrapper = _node_text(node, source)
        if not wrapper.startswith("AETEXT_"):
            continue
        if _disabled_by_literal_zero(node, source) or _inside_preprocessor_header(node):
            continue
        location = _location(node, source, starts, path)
        if wrapper not in WRAPPERS:
            diagnostics.append(
                diagnostic(
                    "AET1011",
                    f"unknown AeText wrapper: {wrapper}",
                    path,
                    int(location["line"]),
                    int(location["column"]),
                )
            )
            continue
        call = node.parent
        if (
            call is None
            or call.type != "call_expression"
            or call.child_by_field_name("function") != node
        ):
            diagnostics.append(
                diagnostic(
                    "AET1012",
                    f"wrapper is not followed by a call: {wrapper}",
                    path,
                    int(location["line"]),
                    int(location["column"]),
                )
            )
            continue
        arguments = call.child_by_field_name("arguments")
        argument_nodes = [] if arguments is None else list(arguments.named_children)
        if arguments is None or arguments.has_error or len(argument_nodes) != 2:
            diagnostics.append(
                diagnostic(
                    "AET1013",
                    f"wrapper requires exactly two balanced arguments: {wrapper}",
                    path,
                    int(location["line"]),
                    int(location["column"]),
                )
            )
            continue
        stable_node = argument_nodes[1]
        stable_id = _node_text(stable_node, source)
        if stable_node.type != "identifier" or not stable_id.startswith("L10N_"):
            diagnostics.append(
                diagnostic(
                    "AET1014",
                    f"wrapper stable ID must be one unexpanded L10N_* identifier: {wrapper}",
                    path,
                    int(location["line"]),
                    int(location["column"]),
                )
            )
            continue
        role, disposition = WRAPPERS[wrapper]
        calls.append(
            {
                "role": role,
                "stableId": stable_id,
                "disposition": disposition,
                "path": path,
                "line": location["line"],
                "column": location["column"],
                "inputOrdinal": input_ordinal,
                "callOrdinal": len(calls),
                "functionName": _function_name(call, source),
            }
        )
    return calls


def _review_layout(calls: list[dict[str, object]]) -> dict[str, object]:
    translated = [call for call in calls if call["disposition"] == "translated"]
    calls_by_id: dict[str, list[dict[str, object]]] = {}
    for call in translated:
        calls_by_id.setdefault(str(call["stableId"]), []).append(call)

    selected: list[tuple[dict[str, object], list[str]]] = []
    for stable_calls in calls_by_id.values():
        panel_calls = [call for call in stable_calls if call["functionName"] == "ParamsSetup"]
        candidates = panel_calls or stable_calls
        first = min(
            candidates,
            key=lambda call: (int(call["inputOrdinal"]), int(call["callOrdinal"])),
        )
        roles: list[str] = []
        for call in sorted(
            stable_calls,
            key=lambda item: (int(item["inputOrdinal"]), int(item["callOrdinal"])),
        ):
            role = str(call["role"])
            if role not in roles:
                roles.append(role)
        selected.append((first, roles))

    sections: list[dict[str, object]] = []
    for role in ROLE_ORDER:
        role_entries = [item for item in selected if str(item[0]["role"]) == role]
        role_entries.sort(
            key=lambda item: (
                0 if item[0]["functionName"] == "ParamsSetup" else 1,
                int(item[0]["inputOrdinal"]),
                int(item[0]["callOrdinal"]),
                str(item[0]["stableId"]),
            )
        )
        if not role_entries:
            continue
        sections.append(
            {
                "role": role,
                "entries": [
                    {
                        "stableId": str(first["stableId"]),
                        "primaryRole": role,
                        "roles": roles,
                        "panelOrder": index,
                    }
                    for index, (first, roles) in enumerate(role_entries)
                ],
            }
        )
    return {"schemaVersion": 1, "sections": sections}


def _assemble_report(
    macro_definitions: list[MacroDefinition],
    calls: list[dict[str, object]],
    diagnostics: list[dict[str, object]],
) -> dict[str, object]:
    macros_by_id: dict[str, MacroDefinition] = {}
    definitions_by_id: dict[str, list[MacroDefinition]] = {}
    for macro in macro_definitions:
        definitions_by_id.setdefault(macro.stable_id, []).append(macro)
    for stable_id, definitions in definitions_by_id.items():
        macros_by_id[stable_id] = definitions[0]
        for duplicate in definitions[1:]:
            diagnostics.append(
                diagnostic(
                    "AET1016",
                    f"duplicate localization macro definition: {stable_id}",
                    str(duplicate.location["path"]),
                    int(duplicate.location["line"]),
                    int(duplicate.location["column"]),
                )
            )

    policies: dict[str, set[str]] = {}
    for call in calls:
        stable_id = str(call["stableId"])
        policies.setdefault(stable_id, set()).add(str(call["disposition"]))
        if stable_id not in macros_by_id:
            diagnostics.append(
                diagnostic(
                    "AET1017",
                    f"missing localization macro definition: {stable_id}",
                    str(call["path"]),
                    int(call["line"]),
                    int(call["column"]),
                )
            )
    for stable_id, dispositions_for_id in policies.items():
        if len(dispositions_for_id) > 1:
            first = next(call for call in calls if call["stableId"] == stable_id)
            diagnostics.append(
                diagnostic(
                    "AET1018",
                    f"inconsistent binding policy for stable ID: {stable_id}",
                    str(first["path"]),
                    int(first["line"]),
                    int(first["column"]),
                )
            )

    uses: dict[tuple[str, str], list[dict[str, object]]] = {}
    dispositions: dict[tuple[str, str], str] = {}
    for call in calls:
        key = (str(call["role"]), str(call["stableId"]))
        uses.setdefault(key, []).append(
            {"path": call["path"], "line": call["line"], "column": call["column"]}
        )
        dispositions.setdefault(key, str(call["disposition"]))

    bindings: list[dict[str, object]] = []
    role_indices = {role: 0 for role in ROLE_ORDER}
    for role, stable_id in sorted(uses, key=lambda item: (ROLE_ORDER[item[0]], item[1])):
        macro = macros_by_id.get(stable_id)
        binding: dict[str, object] = {
            "role": role,
            "stableId": stable_id,
            "disposition": dispositions[(role, stable_id)],
            "index": role_indices[role],
            "uses": sorted(
                uses[(role, stable_id)],
                key=lambda item: (
                    str(item["path"]),
                    int(item["line"]),
                    int(item["column"]),
                ),
            ),
        }
        if macro is not None:
            binding["original"] = macro.original
            binding["definition"] = macro.location
        bindings.append(binding)
        role_indices[role] += 1

    calls.sort(key=lambda item: (int(item["inputOrdinal"]), int(item["callOrdinal"])))
    diagnostics.sort(
        key=lambda item: (
            str(item["path"]),
            int(item["line"]),
            int(item["column"]),
            str(item["code"]),
            str(item["message"]),
        )
    )
    return {
        "schemaVersion": 1,
        "bindings": bindings,
        "calls": calls,
        "reviewLayout": _review_layout(calls),
        "diagnostics": diagnostics,
    }


def scan_sources_treesitter(
    paths: Iterable[str | Path],
    *,
    project_root: str | Path,
) -> dict[str, object]:
    """Scan explicit project inputs using Tree-sitter C++ and return the legacy report shape."""

    root_path = Path(project_root)
    diagnostics: list[dict[str, object]] = []
    macro_definitions: list[MacroDefinition] = []
    calls: list[dict[str, object]] = []
    seen_paths: set[Path] = set()
    parser = Parser(_CPP_LANGUAGE)

    for input_ordinal, supplied in enumerate(paths):
        path = Path(supplied).resolve()
        if path in seen_paths:
            continue
        seen_paths.add(path)
        display_path = relative_path(path, root_path)
        try:
            text = path.read_text(encoding="utf-8-sig")
            source = text.encode("utf-8")
        except (OSError, UnicodeError) as error:
            diagnostics.append(
                diagnostic("AET1015", f"cannot read source: {error}", display_path, 1, 1)
            )
            continue
        starts = _line_starts(source)
        tree = parser.parse(source)
        macro_definitions.extend(
            _scan_macros(tree.root_node, source, starts, display_path, diagnostics)
        )
        calls.extend(
            _scan_calls(
                tree.root_node,
                source,
                starts,
                display_path,
                input_ordinal,
                diagnostics,
            )
        )

    return _assemble_report(macro_definitions, calls, diagnostics)
