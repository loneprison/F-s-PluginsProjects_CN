"""Pure project-tree construction for the review workspace."""

from __future__ import annotations

from collections import defaultdict

from ..catalog.review import ReviewProgress, ReviewProject, ReviewWorkspace
from .i18n import UiText


def _progress_label(progress: ReviewProgress | None, text: UiText) -> str:
    return (
        text.text("tree.unscanned") if progress is None else f"{progress.valid} / {progress.total}"
    )


def _leaf_icon(project: ReviewProject, progress: ReviewProgress | None) -> tuple[str, str]:
    if project.scan_state in {"invalid", "error"}:
        return "error", "red"
    if project.scan_state == "unscanned":
        return "radio_button_unchecked", "grey"
    if progress is None:
        return "radio_button_unchecked", "grey"
    if progress.errors:
        return "error", "red"
    if progress.total and progress.reviewed == progress.total:
        return "check_circle", "green"
    if progress.pending_review:
        return "circle", "orange"
    return "check_circle_outline", "green"


def _aggregate(projects: list[ReviewProject], locale: str, text: UiText) -> str:
    values = [project.progress.get(locale) for project in projects]
    known = [value for value in values if value is not None]
    if not known:
        return text.text("tree.unscanned")
    return f"{sum(value.valid for value in known)} / {sum(value.total for value in known)}"


def project_tree_nodes(
    workspace: ReviewWorkspace,
    locale: str,
    text: UiText,
    search: str = "",
    dirty_projects: set[str] | None = None,
) -> list[dict[str, object]]:
    dirty = dirty_projects or set()
    query = search.strip().casefold()
    filtered = [
        project for project in workspace.projects if not query or query in project.name.casefold()
    ]
    roles: dict[str, list[ReviewProject]] = defaultdict(list)
    for project in filtered:
        roles[project.role].append(project)

    result: list[dict[str, object]] = []
    seen_roles: list[str] = []
    for project in workspace.projects:
        if project.role in roles and project.role not in seen_roles:
            seen_roles.append(project.role)
    for role in seen_roles:
        role_projects = roles[role]
        categories: dict[str, list[ReviewProject]] = defaultdict(list)
        for project in role_projects:
            categories[project.category_label].append(project)
        role_children: list[dict[str, object]] = []
        for category, category_projects in categories.items():
            leaves: list[dict[str, object]] = []
            for project in category_projects:
                progress = project.progress.get(locale)
                icon, color = _leaf_icon(project, progress)
                state_label = (
                    text.text("tree.settings")
                    if project.catalog_kind == "settings" and progress is None
                    else _progress_label(progress, text)
                )
                leaves.append(
                    {
                        "id": f"project:{project.name}",
                        "label": f"{'* ' if project.name in dirty else ''}"
                        f"{project.name}    {state_label}",
                        "icon": icon,
                        "color": color,
                    }
                )
            if category:
                role_children.append(
                    {
                        "id": f"category:{role}:{category}",
                        "label": f"{category}    {_aggregate(category_projects, locale, text)}",
                        "children": leaves,
                    }
                )
            else:
                role_children.extend(leaves)
        result.append(
            {
                "id": f"role:{role}",
                "label": f"{text.text(f'role.{role}')}    "
                f"{_aggregate(role_projects, locale, text)}",
                "children": role_children,
            }
        )
    return result


def project_name_from_node(node_id: str | None) -> str | None:
    prefix = "project:"
    return node_id[len(prefix) :] if node_id and node_id.startswith(prefix) else None
