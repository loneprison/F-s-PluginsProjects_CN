from __future__ import annotations

from pathlib import Path

from aetext import scan_sources

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]


def test_tree_sitter_handles_bounded_fixture(tmp_path: Path) -> None:
    source = r"""
#define L10N_PARAM_ALPHA "Alpha"
#define L10N_SHARED "Shared"
auto nested = AETEXT_PARAM(call(1, 2), L10N_PARAM_ALPHA);
auto label = AETEXT_LABEL(strings, L10N_SHARED);
/* AETEXT_TOPIC(strings, L10N_IGNORED) */
#if 0
auto disabled = AETEXT_POPUP(strings, L10N_IGNORED);
#else
auto enabled = AETEXT_PARAM(strings, L10N_SHARED);
#endif
"""
    path = tmp_path / "fixture.cpp"
    path.write_text(source, encoding="utf-8")

    report = scan_sources([path], project_root=tmp_path)

    assert report["diagnostics"] == []
    assert len(report["bindings"]) == 3
    assert len(report["calls"]) == 3


def test_tree_sitter_scans_plugin_skeleton_contract() -> None:
    paths = [
        REPOSITORY_ROOT / "PluginSkeleton" / "PluginSkeleton.h",
        REPOSITORY_ROOT / "PluginSkeleton" / "PluginSkeleton.cpp",
        REPOSITORY_ROOT / "PluginSkeleton" / "Fs_Entry.h",
        REPOSITORY_ROOT / "PluginSkeleton" / "Fs_Target.h",
    ]

    report = scan_sources(paths, project_root=REPOSITORY_ROOT)

    assert report["diagnostics"] == []
    assert len(report["bindings"]) == 22
    assert len(report["calls"]) == 24
    sections = {section["role"]: section for section in report["reviewLayout"]["sections"]}
    assert [entry["stableId"] for entry in sections["Param"]["entries"]] == [
        "L10N_PARAM_R",
        "L10N_PARAM_G",
        "L10N_PARAM_B",
        "L10N_PARAM_NOISE",
        "L10N_PARAM_NOISE_FRAME",
        "L10N_PARAM_NOISE_OFFSET",
        "L10N_PARAM_HIDDEN_UI",
        "L10N_PARAM_COLOR",
        "L10N_PARAM_ADD_SLIDER",
        "L10N_PARAM_FIXED_SLIDER",
        "L10N_PARAM_FLOAT_SLIDER",
        "L10N_PARAM_CHECKBOX",
        "L10N_PARAM_ANGLE",
        "L10N_PARAM_POPUP",
        "L10N_PARAM_POINT",
        "L10N_PARAM_BUTTON",
    ]
    assert [entry["stableId"] for entry in sections["Label"]["entries"]] == [
        "L10N_PARAM_ON",
        "L10N_PARAM_HIDDEN_TEXT",
        "L10N_PARAM_PUSH",
    ]
    assert [
        (binding["stableId"], binding["index"])
        for binding in report["bindings"]
        if binding["role"] == "Param"
    ] == [
        (stable_id, index)
        for index, stable_id in enumerate(
            sorted(entry["stableId"] for entry in sections["Param"]["entries"])
        )
    ]


def test_review_layout_prefers_params_setup_and_deduplicates_cross_role_id(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.cpp"
    second = tmp_path / "second.cpp"
    first.write_text(
        '#define L10N_SHARED "Shared"\nvoid Helper() { AETEXT_LABEL(strings, L10N_SHARED); }\n',
        encoding="utf-8",
    )
    second.write_text(
        "PF_Err Fixture::ParamsSetup() {\n"
        "  AETEXT_PARAM(strings, L10N_SHARED);\n"
        "  AETEXT_LABEL(strings, L10N_SHARED);\n"
        "  return 0;\n"
        "}\n",
        encoding="utf-8",
    )

    report = scan_sources([first, second], project_root=tmp_path)

    assert report["diagnostics"] == []
    assert [(item["role"], item["index"]) for item in report["bindings"]] == [
        ("Param", 0),
        ("Label", 0),
    ]
    sections = report["reviewLayout"]["sections"]
    assert sections == [
        {
            "role": "Param",
            "entries": [
                {
                    "stableId": "L10N_SHARED",
                    "primaryRole": "Param",
                    "roles": ["Label", "Param"],
                    "panelOrder": 0,
                }
            ],
        }
    ]
    assert [
        (call["inputOrdinal"], call["callOrdinal"], call["functionName"])
        for call in report["calls"]
    ] == [
        (0, 0, "Helper"),
        (1, 0, "ParamsSetup"),
        (1, 1, "ParamsSetup"),
    ]
