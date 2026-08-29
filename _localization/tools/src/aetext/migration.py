"""Deterministic comparison helpers for legacy binding migration reports."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import tempfile
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from tempfile import TemporaryDirectory

from tree_sitter import Node, Parser

from .catalog.formatting import format_catalog_json
from .core.scanner_contract import (
    diagnostic as _diagnostic,
)
from .core.scanner_contract import (
    relative_path as _relative_path,
)
from .scanner import scan_sources
from .scanner_treesitter import (
    _CPP_LANGUAGE,
    _disabled_by_literal_zero,
    _line_starts,
    _node_text,
    _position,
    _walk,
)
from .schema import canonicalize_role_sections

_ROLES = ("Param", "Label", "Popup", "Topic", "About", "Error")
_LEGACY_ROLE_PATTERN = re.compile(
    r"::(?:Param|Label|Popup|Topic|About|Error)Text::[A-Za-z_][A-Za-z0-9_]*"
)


def _entries(report: object) -> list[Mapping[str, object]]:
    if not isinstance(report, Mapping):
        return []
    bindings = report.get("bindings")
    if not isinstance(bindings, Mapping):
        return []
    entries = bindings.get("entries")
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes, bytearray)):
        return []
    return [entry for entry in entries if isinstance(entry, Mapping)]


def _by_key(report: object) -> dict[tuple[str, str], Mapping[str, object]]:
    result: dict[tuple[str, str], Mapping[str, object]] = {}
    for entry in _entries(report):
        role = entry.get("role")
        stable_id = entry.get("stableId")
        if isinstance(role, str) and isinstance(stable_id, str):
            result[(role, stable_id)] = entry
    return result


def _roles_by_id(entries: Mapping[tuple[str, str], object]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for role, stable_id in entries:
        result.setdefault(stable_id, set()).add(role)
    return result


def compare_legacy_baseline(baseline: object, generated: object) -> dict[str, object]:
    """Compare reports by Role + stable ID and exact legacy/UTF-8 byte maps."""

    expected = _by_key(baseline)
    actual = _by_key(generated)
    expected_keys = set(expected)
    actual_keys = set(actual)
    expected_roles = _roles_by_id(expected)
    actual_roles = _roles_by_id(actual)

    role_mismatches = [
        {
            "stableId": stable_id,
            "expectedRoles": sorted(expected_roles[stable_id]),
            "actualRoles": sorted(actual_roles[stable_id]),
        }
        for stable_id in sorted(set(expected_roles) & set(actual_roles))
        if expected_roles[stable_id] != actual_roles[stable_id]
    ]
    mismatched_ids = {item["stableId"] for item in role_mismatches}
    missing = [
        {"role": role, "stableId": stable_id}
        for role, stable_id in sorted(expected_keys - actual_keys)
        if stable_id not in mismatched_ids
    ]
    extra = [
        {"role": role, "stableId": stable_id}
        for role, stable_id in sorted(actual_keys - expected_keys)
        if stable_id not in mismatched_ids
    ]

    byte_changes: list[dict[str, object]] = []
    for role, stable_id in sorted(expected_keys & actual_keys):
        expected_entry = expected[(role, stable_id)]
        actual_entry = actual[(role, stable_id)]
        for field in ("legacyHex", "utf8Hex"):
            expected_bytes = expected_entry.get(field)
            actual_bytes = actual_entry.get(field)
            if expected_bytes != actual_bytes:
                byte_changes.append(
                    {
                        "role": role,
                        "stableId": stable_id,
                        "representation": field,
                        "expected": expected_bytes,
                        "actual": actual_bytes,
                    }
                )

    result: dict[str, object] = {
        "missing": missing,
        "extra": extra,
        "roleMismatches": role_mismatches,
        "byteChanges": byte_changes,
    }
    result["ok"] = not any(result[field] for field in result)
    return result


def _legacy_bindings(catalog: object) -> tuple[dict[tuple[str, str], str], list[dict[str, object]]]:
    diagnostics: list[dict[str, object]] = []
    result: dict[tuple[str, str], str] = {}
    if not isinstance(catalog, Mapping):
        return result, [_diagnostic("AET5001", "legacy catalog root must be an object", "", 1, 1)]
    bindings = catalog.get("bindings")
    if not isinstance(bindings, Mapping):
        return result, [
            _diagnostic("AET5002", "legacy catalog bindings must be an object", "", 1, 1)
        ]
    for role, role_bindings in bindings.items():
        if role not in _ROLES or not isinstance(role_bindings, Mapping):
            diagnostics.append(
                _diagnostic("AET5003", f"invalid legacy binding Role: {role}", "", 1, 1)
            )
            continue
        for token, stable_id in role_bindings.items():
            if not isinstance(token, str) or not isinstance(stable_id, str):
                diagnostics.append(
                    _diagnostic(
                        "AET5004",
                        f"invalid legacy binding: role={role} token={token}",
                        "",
                        1,
                        1,
                    )
                )
                continue
            result[(str(role), token)] = stable_id
    return result, diagnostics


def _old_accessor_edit(
    call: Node,
    source: bytes,
    starts: list[int],
    namespace: str,
    bindings: Mapping[tuple[str, str], str],
    path: str,
) -> dict[str, object] | None:
    function = call.child_by_field_name("function")
    arguments = call.child_by_field_name("arguments")
    if function is None or function.type != "field_expression" or arguments is None:
        return None
    receiver = function.child_by_field_name("argument")
    field = function.child_by_field_name("field")
    if receiver is None or receiver.type != "identifier" or field is None:
        return None
    role = _node_text(field, source)
    if role not in _ROLES or arguments.has_error or len(arguments.named_children) != 1:
        return None
    argument = arguments.named_children[0]
    expected_type = role + "Text"
    if argument.type != "qualified_identifier":
        return None
    argument_scope = argument.child_by_field_name("scope")
    argument_name = argument.child_by_field_name("name")
    if (
        argument_scope is None
        or _node_text(argument_scope, source) != namespace
        or argument_name is None
        or argument_name.type != "qualified_identifier"
    ):
        return None
    type_scope = argument_name.child_by_field_name("scope")
    token = argument_name.child_by_field_name("name")
    if (
        type_scope is None
        or _node_text(type_scope, source) != expected_type
        or token is None
        or token.type != "identifier"
    ):
        return None
    token_name = _node_text(token, source)
    receiver_name = _node_text(receiver, source)
    line, column = _position(source, starts, receiver.start_byte)
    stable_id = bindings.get((role, token_name))
    if stable_id is None:
        return {
            "diagnostic": _diagnostic(
                "AET5005",
                f"legacy accessor has no binding: role={role} token={token_name}",
                path,
                line,
                column,
            )
        }
    replacement = f"AETEXT_{role.upper()}({receiver_name}, {stable_id})"
    return {
        "kind": "binding",
        "path": path,
        "line": line,
        "column": column,
        "role": role,
        "token": token_name,
        "stableId": stable_id,
        "start": len(source[: call.start_byte].decode("utf-8")),
        "end": len(source[: call.end_byte].decode("utf-8")),
        "replacement": replacement,
    }


def _options_edits(
    call: Node,
    source: bytes,
    starts: list[int],
    namespace: str,
    path: str,
) -> tuple[list[dict[str, object]], dict[str, object] | None]:
    function = call.child_by_field_name("function")
    arguments = call.child_by_field_name("arguments")
    if function is None or function.type != "field_expression" or arguments is None:
        return [], None
    receiver = function.child_by_field_name("argument")
    field = function.child_by_field_name("field")
    if (
        receiver is None
        or receiver.type != "identifier"
        or field is None
        or _node_text(field, source) != "Options"
    ):
        return [], None
    if arguments.has_error or len(arguments.named_children) != 1:
        line, column = _position(source, starts, call.start_byte)
        return [], _diagnostic(
            "AET5007",
            "legacy Options call must have exactly one title argument",
            path,
            line,
            column,
        )

    statement = call.parent
    block = statement.parent if statement is not None else None
    declaration = statement.prev_named_sibling if statement is not None else None
    if (
        statement is None
        or statement.type != "expression_statement"
        or block is None
        or block.type != "compound_statement"
        or declaration is None
        or declaration.type != "declaration"
    ):
        line, column = _position(source, starts, call.start_byte)
        return [], _diagnostic(
            "AET5008",
            "legacy Options call is not immediately preceded by its Strings declaration",
            path,
            line,
            column,
        )

    strings_name = _node_text(receiver, source)
    declaration_type = declaration.child_by_field_name("type")
    declarator = declaration.child_by_field_name("declarator")
    if declaration_type is None:
        declaration_type = next(
            (child for child in declaration.named_children if child.type == "qualified_identifier"),
            None,
        )
    if declarator is None:
        declarator = next(
            (child for child in declaration.named_children if child.type == "function_declarator"),
            None,
        )
    declared_name = declarator.child_by_field_name("declarator") if declarator is not None else None
    parameters = declarator.child_by_field_name("parameters") if declarator is not None else None
    constructor_arguments = parameters.named_children if parameters is not None else []
    if (
        declaration_type is None
        or _node_text(declaration_type, source) != f"{namespace}::Strings"
        or declared_name is None
        or _node_text(declared_name, source) != strings_name
        or len(constructor_arguments) != 1
    ):
        line, column = _position(source, starts, call.start_byte)
        return [], _diagnostic(
            "AET5008",
            "legacy Options call has no matching one-argument Strings declaration",
            path,
            line,
            column,
        )

    uses = [
        node
        for node in _walk(block)
        if node.type == "identifier" and _node_text(node, source) == strings_name
    ]
    if len(uses) != 2:
        line, column = _position(source, starts, call.start_byte)
        return [], _diagnostic(
            "AET5009",
            "Options-only Strings declaration has additional uses",
            path,
            line,
            column,
        )

    in_data = _node_text(constructor_arguments[0], source)
    title = _node_text(arguments.named_children[0], source)
    line, column = _position(source, starts, call.start_byte)
    declaration_start = declaration.start_byte
    line_start = source.rfind(b"\n", 0, declaration_start) + 1
    if source[line_start:declaration_start].strip(b" \t"):
        line_start = declaration_start
    return [
        {
            "kind": "optionsDeclaration",
            "path": path,
            "line": line,
            "column": column,
            "start": len(source[:line_start].decode("utf-8")),
            "end": len(source[: declaration.end_byte].decode("utf-8")),
            "replacement": "",
        },
        {
            "kind": "optionsCall",
            "path": path,
            "line": line,
            "column": column,
            "start": len(source[: call.start_byte].decode("utf-8")),
            "end": len(source[: call.end_byte].decode("utf-8")),
            "replacement": f"{namespace}::OpenSettings({in_data}, {title})",
        },
    ], None


def _about_bridge_edit(
    call: Node,
    source: bytes,
    starts: list[int],
    path: str,
) -> dict[str, object] | None:
    function = call.child_by_field_name("function")
    arguments = call.child_by_field_name("arguments")
    if function is None or arguments is None:
        return None
    if function.type == "field_expression":
        field = function.child_by_field_name("field")
        field_name = _node_text(field, source) if field is not None else ""
    elif function.type == "identifier":
        field_name = _node_text(function, source)
    else:
        return None
    values = arguments.named_children
    if (field_name == "About" and len(values) != 6) or (
        field_name == "AboutBox" and len(values) != 5
    ):
        return None
    if field_name not in {"About", "AboutBox"}:
        return None
    script_field = values[-2]
    legacy_field = values[-1]
    if script_field.type != "field_expression" or legacy_field.type != "field_expression":
        return None
    script_receiver = script_field.child_by_field_name("argument")
    legacy_receiver = legacy_field.child_by_field_name("argument")
    script_name = script_field.child_by_field_name("field")
    legacy_name = legacy_field.child_by_field_name("field")
    if (
        script_receiver is None
        or legacy_receiver is None
        or script_name is None
        or legacy_name is None
        or _node_text(script_receiver, source) != _node_text(legacy_receiver, source)
        or _node_text(script_name, source) != "script_utf8"
        or _node_text(legacy_name, source) != "legacy"
    ):
        return None
    line, column = _position(source, starts, script_field.start_byte)
    return {
        "kind": "aboutBridge",
        "path": path,
        "line": line,
        "column": column,
        "start": len(source[: script_field.start_byte].decode("utf-8")),
        "end": len(source[: legacy_field.end_byte].decode("utf-8")),
        "replacement": _node_text(script_receiver, source),
    }


def _unrewritten_legacy_calls(text: str, path: str, namespace: str) -> list[dict[str, object]]:
    source = text.encode("utf-8")
    starts = _line_starts(source)
    root = Parser(_CPP_LANGUAGE).parse(source).root_node
    about_variables: set[str] = set()
    for node in _walk(root):
        if node.type != "call_expression":
            continue
        function = node.child_by_field_name("function")
        if function is None or _node_text(function, source) != "AETEXT_ABOUT":
            continue
        parent = node.parent
        while parent is not None and parent.type not in {"init_declarator", "declaration"}:
            parent = parent.parent
        if parent is not None and parent.type == "init_declarator":
            declarator = parent.child_by_field_name("declarator")
            if declarator is not None and declarator.type == "identifier":
                about_variables.add(_node_text(declarator, source))

    result: list[dict[str, object]] = []
    namespace_prefix = f"{namespace}::"
    for node in _walk(root):
        kind: str | None = None
        if node.type == "field_expression":
            receiver = node.child_by_field_name("argument")
            field = node.child_by_field_name("field")
            receiver_name = _node_text(receiver, source) if receiver is not None else ""
            field_name = _node_text(field, source) if field is not None else ""
            if field_name == "Options":
                kind = "options"
            elif receiver_name in about_variables and field_name == "script_utf8":
                kind = "about-script-field"
            elif receiver_name in about_variables and field_name == "legacy":
                kind = "about-legacy-field"
        elif node.type == "qualified_identifier":
            value = _node_text(node, source)
            if value.startswith(namespace_prefix) and _LEGACY_ROLE_PATTERN.search(value):
                kind = "role-token"
        if kind is None:
            continue
        line, column = _position(source, starts, node.start_byte)
        result.append(
            {
                "path": path,
                "line": line,
                "column": column,
                "kind": kind,
                "text": _node_text(node, source),
            }
        )
    return result


def _plan_file_edits(
    text: str,
    path: str,
    namespace: str,
    bindings: Mapping[tuple[str, str], str],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    diagnostics: list[dict[str, object]] = []
    source = text.encode("utf-8")
    starts = _line_starts(source)
    root = Parser(_CPP_LANGUAGE).parse(source).root_node
    edits: list[dict[str, object]] = []
    calls = sorted(
        (node for node in _walk(root) if node.type == "call_expression"),
        key=lambda node: node.start_byte,
    )
    for call in calls:
        if _disabled_by_literal_zero(call, source):
            continue
        edit = _old_accessor_edit(call, source, starts, namespace, bindings, path)
        if edit is not None:
            diagnostic = edit.get("diagnostic")
            if isinstance(diagnostic, Mapping):
                diagnostics.append(dict(diagnostic))
            else:
                edits.append(edit)
        option_edits, option_diagnostic = _options_edits(call, source, starts, namespace, path)
        edits.extend(option_edits)
        if option_diagnostic is not None:
            diagnostics.append(option_diagnostic)
        about_edit = _about_bridge_edit(call, source, starts, path)
        if about_edit is not None:
            edits.append(about_edit)
    return edits, diagnostics


def _apply_edits(text: str, edits: Sequence[Mapping[str, object]]) -> str:
    result = text
    for edit in sorted(edits, key=lambda item: int(item["start"]), reverse=True):
        start = int(edit["start"])
        end = int(edit["end"])
        result = result[:start] + str(edit["replacement"]) + result[end:]
    return result


def _role_counts(entries: Iterable[Mapping[str, object]]) -> dict[str, int]:
    counts = {role: 0 for role in _ROLES}
    for entry in entries:
        role = entry.get("role")
        if isinstance(role, str) and role in counts:
            counts[role] += 1
    return counts


def _api_edit_counts(edits: Iterable[Mapping[str, object]]) -> dict[str, int]:
    counts = {"aboutBridge": 0, "optionsCall": 0, "optionsDeclaration": 0}
    for edit in edits:
        kind = edit.get("kind")
        if isinstance(kind, str) and kind in counts:
            counts[kind] += 1
    return counts


def plan_legacy_migration(
    catalog: object,
    source_paths: Iterable[str | Path],
    *,
    namespace: str,
    project_root: str | Path,
) -> dict[str, object]:
    """Plan old accessor rewrites, rescan temporary copies, and never edit product files."""

    root = Path(project_root).resolve()
    bindings, diagnostics = _legacy_bindings(catalog)
    source_documents: list[tuple[Path, str, str]] = []
    edits: list[dict[str, object]] = []
    unrewritten_legacy_calls: list[dict[str, object]] = []
    edited_input_sha256: dict[str, str] = {}
    seen_paths: set[Path] = set()
    for supplied in source_paths:
        path = Path(supplied).resolve()
        if path in seen_paths:
            continue
        seen_paths.add(path)
        display = _relative_path(path, root)
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8-sig")
        except (OSError, UnicodeError) as error:
            diagnostics.append(
                _diagnostic("AET5006", f"cannot read migration input: {error}", display, 1, 1)
            )
            continue
        file_edits, file_diagnostics = _plan_file_edits(text, display, namespace, bindings)
        edits.extend(file_edits)
        if file_edits:
            edited_input_sha256[display] = hashlib.sha256(raw).hexdigest().upper()
        diagnostics.extend(file_diagnostics)
        prospective = _apply_edits(text, file_edits)
        if namespace + "::" in prospective or "AETEXT_ABOUT" in prospective:
            unrewritten_legacy_calls.extend(
                _unrewritten_legacy_calls(prospective, display, namespace)
            )
        source_documents.append((path, display, prospective))

    with TemporaryDirectory(prefix="AeTextMigration-") as directory:
        scratch = Path(directory)
        prospective_paths: list[Path] = []
        for index, (_, display, prospective) in enumerate(source_documents):
            relative = Path(display)
            if relative.is_absolute() or ".." in relative.parts:
                relative = Path("external") / f"{index:04d}-{relative.name}"
            target = scratch / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(prospective.encode("utf-8"))
            prospective_paths.append(target)
        scanner_report = scan_sources(prospective_paths, project_root=scratch)

    diagnostics.extend(scanner_report["diagnostics"])
    expected_keys = {(role, stable_id) for (role, _), stable_id in bindings.items()}
    actual_bindings = scanner_report["bindings"]
    actual_keys = {(str(entry["role"]), str(entry["stableId"])) for entry in actual_bindings}
    expected_roles = _roles_by_id({key: None for key in expected_keys})
    actual_roles = _roles_by_id({key: None for key in actual_keys})
    role_mismatches = [
        {
            "stableId": stable_id,
            "expectedRoles": sorted(expected_roles[stable_id]),
            "actualRoles": sorted(actual_roles[stable_id]),
        }
        for stable_id in sorted(set(expected_roles) & set(actual_roles))
        if expected_roles[stable_id] != actual_roles[stable_id]
    ]
    mismatched_ids = {str(item["stableId"]) for item in role_mismatches}
    missing = [
        {"role": role, "stableId": stable_id}
        for role, stable_id in sorted(expected_keys - actual_keys)
        if stable_id not in mismatched_ids
    ]
    extra = [
        {"role": role, "stableId": stable_id}
        for role, stable_id in sorted(actual_keys - expected_keys)
        if stable_id not in mismatched_ids
    ]
    call_count_mismatch = None
    binding_edits = [edit for edit in edits if edit.get("kind") == "binding"]
    if len(binding_edits) != len(scanner_report["calls"]):
        call_count_mismatch = {
            "legacyCalls": len(binding_edits),
            "prospectiveCalls": len(scanner_report["calls"]),
        }

    public_edits = [
        {key: value for key, value in edit.items() if key not in ("start", "end")} for edit in edits
    ]
    equivalence = {
        "missing": missing,
        "extra": extra,
        "roleMismatches": role_mismatches,
        "callCountMismatch": call_count_mismatch,
        "byteComparison": "not-run",
    }
    return {
        "schemaVersion": 1,
        "mode": "dry-run",
        "namespace": namespace,
        "legacy": {
            "bindingCount": len(expected_keys),
            "bindingRoleCounts": _role_counts(
                {"role": role, "stableId": stable_id} for role, stable_id in expected_keys
            ),
            "callCount": len(binding_edits),
            "callRoleCounts": _role_counts(binding_edits),
        },
        "prospective": {
            "bindingCount": len(actual_bindings),
            "bindingRoleCounts": _role_counts(actual_bindings),
            "callCount": len(scanner_report["calls"]),
            "callRoleCounts": _role_counts(scanner_report["calls"]),
        },
        "edits": public_edits,
        "apiEditCounts": _api_edit_counts(edits),
        "editedInputSha256": edited_input_sha256,
        "unrewrittenLegacyCalls": sorted(
            unrewritten_legacy_calls,
            key=lambda item: (
                str(item.get("path", "")),
                int(item.get("line", 0)),
                int(item.get("column", 0)),
                str(item.get("kind", "")),
            ),
        ),
        "equivalence": equivalence,
        "diagnostics": sorted(
            diagnostics,
            key=lambda item: (
                str(item.get("path", "")),
                int(item.get("line", 0)),
                int(item.get("column", 0)),
                str(item.get("code", "")),
            ),
        ),
        "readyForByteComparison": not (
            missing or extra or role_mismatches or call_count_mismatch or diagnostics
        ),
        "readyForBindingRemoval": False,
    }


def _atomic_write(path: Path, contents: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=path.name + ".tmp.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(contents)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def apply_legacy_migration(
    catalog_path: str | Path,
    source_paths: Iterable[str | Path],
    *,
    namespace: str,
    project_root: str | Path,
    equivalence_report: object,
) -> dict[str, object]:
    """Apply only a previously proven migration, replacing the catalog last."""

    root = Path(project_root).resolve()
    catalog_file = Path(catalog_path).resolve()
    raw_catalog = catalog_file.read_bytes()
    catalog = json.loads(raw_catalog.decode("utf-8-sig"))
    if not isinstance(equivalence_report, Mapping) or not equivalence_report.get(
        "readyForBindingRemoval"
    ):
        raise ValueError("equivalence report does not permit binding removal")
    expected_catalog_hash = equivalence_report.get("catalogSha256")
    actual_catalog_hash = hashlib.sha256(raw_catalog).hexdigest().upper()
    if expected_catalog_hash != actual_catalog_hash:
        raise ValueError("catalog changed after equivalence validation")

    bindings, diagnostics = _legacy_bindings(catalog)
    if diagnostics:
        raise ValueError("legacy catalog is not valid for migration")
    expected_source_hashes = equivalence_report.get("editedInputSha256")
    if not isinstance(expected_source_hashes, Mapping):
        raise ValueError("equivalence report has no bound source hashes")

    prepared: list[tuple[Path, bytes]] = []
    binding_edit_count = 0
    api_edit_counts = {"aboutBridge": 0, "optionsCall": 0, "optionsDeclaration": 0}
    unrewritten_legacy_calls: list[dict[str, object]] = []
    seen_paths: set[Path] = set()
    for supplied in source_paths:
        path = Path(supplied).resolve()
        if path in seen_paths:
            continue
        seen_paths.add(path)
        raw = path.read_bytes()
        has_bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
        display = _relative_path(path, root)
        edits, file_diagnostics = _plan_file_edits(text, display, namespace, bindings)
        if file_diagnostics:
            raise ValueError(f"migration source diagnostics: {display}")
        if not edits:
            continue
        expected_hash = expected_source_hashes.get(display)
        actual_hash = hashlib.sha256(raw).hexdigest().upper()
        if expected_hash != actual_hash:
            raise ValueError(f"source changed after equivalence validation: {display}")
        prospective = _apply_edits(text, edits).encode("utf-8")
        prepared.append((path, (b"\xef\xbb\xbf" if has_bom else b"") + prospective))
        binding_edit_count += sum(edit.get("kind") == "binding" for edit in edits)
        for kind, count in _api_edit_counts(edits).items():
            api_edit_counts[kind] += count
        prospective_text = prospective.decode("utf-8")
        if namespace + "::" in prospective_text or "AETEXT_ABOUT" in prospective_text:
            unrewritten_legacy_calls.extend(
                _unrewritten_legacy_calls(prospective_text, display, namespace)
            )

    if binding_edit_count != equivalence_report.get("migratedCallCount"):
        raise ValueError("live migration call count no longer matches the equivalence report")
    if api_edit_counts != equivalence_report.get("apiEditCounts"):
        raise ValueError("live migration API edit counts no longer match the equivalence report")
    if unrewritten_legacy_calls:
        raise ValueError("live migration still contains unrewritten legacy calls")
    if not isinstance(catalog, Mapping) or not isinstance(catalog.get("translations"), Mapping):
        raise ValueError("legacy catalog translations must be an object")
    final_translations = copy.deepcopy(catalog["translations"])
    source_selections = equivalence_report.get("explicitSourceSelectionsAdded", [])
    if not isinstance(source_selections, Sequence):
        raise ValueError("equivalence report source selections must be an array")
    for selection in source_selections:
        if not isinstance(selection, Mapping):
            raise ValueError("invalid source selection in equivalence report")
        locale = selection.get("locale")
        stable_id = selection.get("stableId")
        locale_map = final_translations.get(locale)
        if (
            not isinstance(locale, str)
            or not isinstance(stable_id, str)
            or not isinstance(locale_map, dict)
        ):
            raise ValueError("invalid source selection target in equivalence report")
        if stable_id in locale_map:
            raise ValueError(
                f"source selection would overwrite an existing value: {locale}.{stable_id}"
            )
        locale_map[stable_id] = {"useSource": True}

    review_layout = equivalence_report.get("reviewLayout")
    generated_bindings = equivalence_report.get("generatedBindings")
    if not isinstance(review_layout, Mapping) or not isinstance(generated_bindings, Sequence):
        raise ValueError("equivalence report has no source-derived ReviewLayout")
    ordered_translations: dict[str, object] = {}
    for locale, locale_map in final_translations.items():
        if not isinstance(locale, str) or not isinstance(locale_map, Mapping):
            raise ValueError("legacy catalog locale must be an object")
        ordered_translations[locale] = canonicalize_role_sections(
            locale_map,
            review_layout,
            generated_bindings,
        )

    final_catalog = format_catalog_json(
        {"schemaVersion": 1, "translations": ordered_translations}
    ).encode("utf-8")

    for path, contents in prepared:
        _atomic_write(path, contents)
    _atomic_write(catalog_file, final_catalog)
    return {
        "sourceFilesModified": [_relative_path(path, root) for path, _ in prepared],
        "callsMigrated": binding_edit_count,
        "apiEditCounts": api_edit_counts,
        "catalogModified": _relative_path(catalog_file, root),
    }


def materialize_legacy_migration(
    catalog: object,
    family: object,
    source_paths: Iterable[str | Path],
    *,
    namespace: str,
    project_root: str | Path,
    destination: str | Path,
) -> dict[str, object]:
    """Create a disposable prospective source manifest without editing product files."""

    root = Path(project_root).resolve()
    target_root = Path(destination).resolve()
    if target_root.exists():
        shutil.rmtree(target_root)
    source_root = target_root / "sources"
    source_root.mkdir(parents=True)

    bindings, diagnostics = _legacy_bindings(catalog)
    prospective_paths: list[Path] = []
    binding_edit_count = 0
    all_edits: list[dict[str, object]] = []
    unrewritten_legacy_calls: list[dict[str, object]] = []
    seen_paths: set[Path] = set()
    for index, supplied in enumerate(source_paths):
        path = Path(supplied).resolve()
        if path in seen_paths:
            continue
        seen_paths.add(path)
        display = _relative_path(path, root)
        raw = path.read_bytes()
        has_bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
        edits, file_diagnostics = _plan_file_edits(text, display, namespace, bindings)
        diagnostics.extend(file_diagnostics)
        all_edits.extend(edits)
        binding_edit_count += sum(edit.get("kind") == "binding" for edit in edits)
        prospective = _apply_edits(text, edits)
        if namespace + "::" in prospective or "AETEXT_ABOUT" in prospective:
            unrewritten_legacy_calls.extend(
                _unrewritten_legacy_calls(prospective, display, namespace)
            )
        target = source_root / f"{index:04d}-{path.name}"
        encoded = prospective.encode("utf-8")
        target.write_bytes((b"\xef\xbb\xbf" if has_bom else b"") + encoded)
        prospective_paths.append(target)

    if diagnostics:
        raise ValueError("prospective migration has scanner diagnostics")
    if not isinstance(catalog, Mapping) or not isinstance(catalog.get("translations"), Mapping):
        raise ValueError("legacy catalog translations must be an object")

    prospective_translations = copy.deepcopy(catalog["translations"])
    explicit_source_selections: list[dict[str, str]] = []
    scanner_report = scan_sources(prospective_paths, project_root=target_root)
    if scanner_report["diagnostics"]:
        raise ValueError("prospective source selection scan has diagnostics")
    if not isinstance(family, Mapping) or family.get("familyId") != "fs":
        raise ValueError("legacy implicit source migration is defined only for the F's family")
    variants = family.get("variants")
    if not isinstance(variants, Sequence):
        raise ValueError("family variants must be an array")
    for variant in variants:
        if not isinstance(variant, Mapping):
            continue
        text_source = variant.get("textSource")
        if (
            not isinstance(text_source, Mapping)
            or text_source.get("kind") != "translation"
            or text_source.get("locale") != "en"
            or variant.get("encodingProfile") != "windows-1252"
        ):
            continue
        locale_map = prospective_translations.get("en")
        if not isinstance(locale_map, dict):
            raise ValueError("legacy F's catalog translations.en must be an object")
        for binding in scanner_report["bindings"]:
            if binding.get("disposition") != "translated":
                continue
            stable_id = str(binding["stableId"])
            if stable_id in locale_map:
                continue
            try:
                str(binding["original"]).encode("cp1252", errors="strict")
            except UnicodeEncodeError as error:
                raise ValueError(
                    f"legacy implicit English source is not CP1252 encodable: {stable_id}"
                ) from error
            locale_map[stable_id] = {"useSource": True}
            explicit_source_selections.append({"locale": "en", "stableId": stable_id})

    ordered_translations: dict[str, object] = {}
    for locale, locale_map in prospective_translations.items():
        if not isinstance(locale, str) or not isinstance(locale_map, Mapping):
            raise ValueError("legacy catalog locale must be an object")
        ordered_translations[locale] = canonicalize_role_sections(
            locale_map,
            scanner_report["reviewLayout"],
            scanner_report["bindings"],
        )

    prospective_catalog = {
        "schemaVersion": 1,
        "translations": ordered_translations,
    }
    catalog_path = target_root / "catalog.json"
    catalog_path.write_text(
        format_catalog_json(prospective_catalog),
        encoding="utf-8",
        newline="\n",
    )
    source_list_path = target_root / "sources.txt"
    source_list_path.write_text(
        "\n".join(str(path) for path in prospective_paths) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {
        "catalogPath": str(catalog_path),
        "sourceListPath": str(source_list_path),
        "sourceCount": len(prospective_paths),
        "migratedCallCount": binding_edit_count,
        "apiEditCounts": _api_edit_counts(all_edits),
        "unrewrittenLegacyCalls": sorted(
            unrewritten_legacy_calls,
            key=lambda item: (
                str(item.get("path", "")),
                int(item.get("line", 0)),
                int(item.get("column", 0)),
                str(item.get("kind", "")),
            ),
        ),
        "explicitSourceSelections": sorted(
            explicit_source_selections,
            key=lambda item: (item["locale"], item["stableId"]),
        ),
    }
