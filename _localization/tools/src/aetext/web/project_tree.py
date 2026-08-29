"""Pure project-tree construction for the review workspace."""

from __future__ import annotations

from collections import defaultdict

from ..catalog.review import ReviewProgress, ReviewProject, ReviewWorkspace


def _progress_label(progress: ReviewProgress | None) -> str:
    return "未扫描" if progress is None else f"{progress.valid} / {progress.total}"


def _leaf_icon(project: ReviewProject, progress: ReviewProgress | None) -> tuple[str, str]:
    if project.deferred:
        return "history", "grey"
    if project.scan_state == "legacy":
        return "hourglass_empty", "grey"
    if project.scan_state in {"invalid", "error"}:
        return "error", "red"
    if project.scan_state in {"unscanned", "settings"}:
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


def _aggregate(projects: list[ReviewProject], locale: str) -> str:
    values = [project.progress.get(locale) for project in projects if not project.deferred]
    known = [value for value in values if value is not None]
    if not known:
        return "未扫描"
    return f"{sum(value.valid for value in known)} / {sum(value.total for value in known)}"


def project_tree_nodes(
    workspace: ReviewWorkspace,
    locale: str,
    search: str = "",
) -> list[dict[str, object]]:
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
                    "历史骨架 · 当前迁移非重点"
                    if project.deferred
                    else "待迁移"
                    if project.scan_state == "legacy"
                    else "设置项"
                    if project.scan_state == "settings"
                    else _progress_label(progress)
                )
                leaves.append(
                    {
                        "id": f"project:{project.name}",
                        "label": f"{project.name}    {state_label}",
                        "icon": icon,
                        "color": color,
                    }
                )
            if category:
                role_children.append(
                    {
                        "id": f"category:{role}:{category}",
                        "label": f"{category}    {_aggregate(category_projects, locale)}",
                        "children": leaves,
                    }
                )
            else:
                role_children.extend(leaves)
        result.append(
            {
                "id": f"role:{role}",
                "label": f"{role_projects[0].role_label}    {_aggregate(role_projects, locale)}",
                "children": role_children,
            }
        )
    return result


def project_name_from_node(node_id: str | None) -> str | None:
    prefix = "project:"
    return node_id[len(prefix) :] if node_id and node_id.startswith(prefix) else None
