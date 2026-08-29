from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "_localization" / "tools" / "src"
sys.path.insert(0, str(TOOLS))

try:
    from aetext import (  # type: ignore[import-not-found]
        compare_legacy_baseline,
        materialize_legacy_migration,
        plan_legacy_migration,
        scan_sources,
        synchronize_effect_catalog,
        validate_effect_catalog,
        validate_family_definition,
    )
    from aetext.migration import (
        apply_legacy_migration,  # type: ignore[import-not-found]
    )
except ImportError as error:
    IMPORT_ERROR: ImportError | None = error
else:
    IMPORT_ERROR = None


FS_FAMILY = {
    "schemaVersion": 1,
    "familyId": "fs",
    "sourceVariantId": "source",
    "variants": [
        {
            "id": "en",
            "textSource": {"kind": "translation", "locale": "en"},
            "encodingProfile": "windows-1252",
        },
        {
            "id": "source",
            "textSource": {"kind": "source"},
            "encodingProfile": "windows-932",
        },
        {
            "id": "zh",
            "textSource": {"kind": "translation", "locale": "zh"},
            "encodingProfile": "windows-936",
        },
        {
            "id": "source-cp936-compatible",
            "textSource": {"kind": "source"},
            "encodingProfile": "windows-936-ae-display",
        },
    ],
}


def diagnostic_codes(diagnostics: list[dict[str, object]]) -> list[str]:
    return [str(item["code"]) for item in diagnostics]


class AeTextToolingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if IMPORT_ERROR is not None:
            raise AssertionError(
                "red phase: _localization/tools/src/aetext is not implemented"
            ) from IMPORT_ERROR

    def test_scanner_handles_bounded_cpp_syntax_and_preserves_calls(self) -> None:
        source = r"""
#define L10N_PARAM_ALPHA "Alpha"
#define L10N_SHARED "Shared"
#define L10N_RAW R"tag(AETEXT_ERROR(strings, L10N_IGNORED))tag"

// AETEXT_ERROR(strings, L10N_IGNORED)
const auto alpha = AETEXT_PARAM(
    strings,
    L10N_PARAM_ALPHA);
const auto shared_param = AETEXT_PARAM(strings, L10N_SHARED);
const auto shared_label = AETEXT_LABEL(strings, L10N_SHARED);
/* AETEXT_TOPIC(strings, L10N_IGNORED) */
#if 0
const auto disabled = AETEXT_POPUP(strings, L10N_IGNORED);
#endif
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.cpp"
            path.write_text(source, encoding="utf-8")
            report = scan_sources([path], project_root=Path(directory))

        self.assertEqual([], report["diagnostics"])
        self.assertEqual(3, len(report["calls"]))
        self.assertEqual(
            [
                ("Param", "L10N_PARAM_ALPHA", 0),
                ("Param", "L10N_SHARED", 1),
                ("Label", "L10N_SHARED", 0),
            ],
            [(entry["role"], entry["stableId"], entry["index"]) for entry in report["bindings"]],
        )

    def test_scanner_accepts_crlf_spliced_string_literal(self) -> None:
        source = (
            b'#define UNRELATED_SCRIPT "first\\\r\n'
            b"second\\\r\n"
            b'third"\r\n'
            b'#define L10N_PARAM_VALUE "Value"\r\n'
            b"auto value = AETEXT_PARAM(strings, L10N_PARAM_VALUE);\r\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "spliced.cpp"
            path.write_bytes(source)
            report = scan_sources([path], project_root=root)

        self.assertEqual([], report["diagnostics"])
        self.assertEqual(1, len(report["calls"]))
        self.assertEqual("L10N_PARAM_VALUE", report["bindings"][0]["stableId"])

    def test_index_order_does_not_depend_on_path_or_line(self) -> None:
        first = """
#define L10N_PARAM_Z "Z"
#define L10N_PARAM_A "A"
auto z = AETEXT_PARAM(strings, L10N_PARAM_Z);
auto a = AETEXT_PARAM(strings, L10N_PARAM_A);
"""
        moved = """


#define L10N_PARAM_A "A"
#define L10N_PARAM_Z "Z"
auto a = AETEXT_PARAM(strings, L10N_PARAM_A);
auto z = AETEXT_PARAM(strings, L10N_PARAM_Z);
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_path = root / "z.cpp"
            moved_path = root / "a.cpp"
            first_path.write_text(first, encoding="utf-8")
            first_report = scan_sources([first_path], project_root=root)
            first_path.unlink()
            moved_path.write_text(moved, encoding="utf-8")
            moved_report = scan_sources([moved_path], project_root=root)

        def keys(report: dict[str, object]) -> list[tuple[str, str, int]]:
            return [
                (entry["role"], entry["stableId"], entry["index"])
                for entry in report["bindings"]  # type: ignore[index]
            ]

        self.assertEqual(keys(first_report), keys(moved_report))
        self.assertEqual(
            [("Param", "L10N_PARAM_A", 0), ("Param", "L10N_PARAM_Z", 1)],
            keys(first_report),
        )

    def test_duplicate_macro_definition_is_structural_even_when_equal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.h"
            second = root / "second.h"
            first.write_text('#define L10N_DUPLICATE "Same"\n', encoding="utf-8")
            second.write_text(
                '#define L10N_DUPLICATE "Same"\n'
                "auto value = AETEXT_PARAM(strings, L10N_DUPLICATE);\n",
                encoding="utf-8",
            )
            report = scan_sources([first, second], project_root=root)

        self.assertTrue(
            any(code.startswith("AET1") for code in diagnostic_codes(report["diagnostics"]))
        )

    def test_translated_and_verbatim_mixture_is_structural(self) -> None:
        source = """
#define L10N_SHARED "Shared"
auto translated = AETEXT_PARAM(strings, L10N_SHARED);
auto verbatim = AETEXT_VERBATIM_LABEL(strings, L10N_SHARED);
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "mixed.cpp"
            path.write_text(source, encoding="utf-8")
            report = scan_sources([path], project_root=root)

        diagnostics = report["diagnostics"]
        self.assertTrue(
            any(
                str(item["code"]).startswith("AET1")
                and "inconsistent binding policy" in str(item["message"])
                for item in diagnostics
            )
        )

    def test_family_schema_accepts_fs_and_has_no_global_locale_whitelist(self) -> None:
        self.assertEqual([], validate_family_definition(copy.deepcopy(FS_FAMILY)))
        future_nf = {
            "schemaVersion": 1,
            "familyId": "fixture-nf",
            "sourceVariantId": "source",
            "variants": [
                {
                    "id": "source",
                    "textSource": {"kind": "source"},
                    "encodingProfile": "windows-1252",
                },
                {
                    "id": "zh",
                    "textSource": {"kind": "translation", "locale": "zh"},
                    "encodingProfile": "windows-936",
                },
            ],
        }
        self.assertEqual([], validate_family_definition(future_nf))

    def test_effect_locales_are_derived_from_the_family(self) -> None:
        bindings = [
            {
                "role": "Param",
                "stableId": "L10N_VALUE",
                "disposition": "translated",
                "original": "Value",
            }
        ]
        fs_catalog = {
            "schemaVersion": 1,
            "translations": {
                "en": {"Param": {"L10N_VALUE": {"useSource": True}}},
                "zh": {"Param": {"L10N_VALUE": "值"}},
            },
            "workflow": {"zh": {"Param": {"L10N_VALUE": "reviewed"}}},
        }
        self.assertEqual(
            [],
            validate_effect_catalog(fs_catalog, FS_FAMILY, bindings, publication=True),
        )

        future_nf = {
            "schemaVersion": 1,
            "familyId": "fixture-nf",
            "sourceVariantId": "source",
            "variants": [
                {
                    "id": "source",
                    "textSource": {"kind": "source"},
                    "encodingProfile": "windows-1252",
                },
                {
                    "id": "zh",
                    "textSource": {"kind": "translation", "locale": "zh"},
                    "encodingProfile": "windows-936",
                },
            ],
        }
        nf_catalog = {
            "schemaVersion": 1,
            "translations": {"zh": {"Param": {"L10N_VALUE": "值"}}},
        }
        self.assertEqual(
            [],
            validate_effect_catalog(nf_catalog, future_nf, bindings, publication=True),
        )

    def test_review_cache_is_not_a_build_or_generator_input(self) -> None:
        build_inputs = [
            ROOT / "Directory.Build.Targets",
            ROOT / "_localization" / "GenerateTextCatalog.ps1",
            *(ROOT / "_localization" / "generator").glob("*.ps1"),
        ]
        for path in build_inputs:
            text = path.read_text(encoding="utf-8-sig").casefold()
            self.assertNotIn("aetext-review", text, path)
            self.assertNotIn("_localization/.cache", text.replace("\\", "/"), path)

    def test_filter_about_keeps_encoding_representations_inside_cae(self) -> None:
        entry = (ROOT / "Filter" / "Filter_Entry.h").read_text(encoding="utf-8-sig")
        cae = (ROOT / "FsLibrary_next" / "CAE.h").read_text(encoding="utf-8-sig")
        compact_cae = " ".join(cae.split())

        self.assertIn("AETEXT_ABOUT(strings, L10N_PLUGIN_DESC)", entry)
        self.assertIn("description);", entry)
        self.assertNotIn("description.script_utf8", entry)
        self.assertNotIn("description.legacy", entry)
        self.assertIn("const AeText::AboutText &description", compact_cae)
        self.assertIn("const AeText::LegacyAboutText &description", compact_cae)
        self.assertIn("AeText::detail::AboutTextAccess::ScriptUtf8(description)", compact_cae)
        self.assertIn("FS_DESCRIPTION, FS_DESCRIPTION, TRUE);", compact_cae)
        self.assertIn("description.script_utf8, description.legacy, FALSE);", compact_cae)
        self.assertIn("scriptCode, platform_encodingB, NULL, NULL", compact_cae)

    def test_filter_uses_the_single_shared_fs_about_definition(self) -> None:
        shared_path = ROOT / "FsLibrary" / "FsAbout.h"
        filter_about_path = ROOT / "Filter" / "FilterAbout.h"
        fs_ae = (ROOT / "FsLibrary" / "FsAE.h").read_text(encoding="utf-8-sig")
        cae = (ROOT / "FsLibrary_next" / "CAE.h").read_text(encoding="utf-8-sig")
        target = (ROOT / "Filter" / "Filter_Target.h").read_text(encoding="utf-8-sig")
        project = (ROOT / "Filter" / "Win" / "Filter.vcxproj").read_text(encoding="utf-8-sig")
        filters = (ROOT / "Filter" / "Win" / "Filter.vcxproj.filters").read_text(
            encoding="utf-8-sig"
        )

        self.assertTrue(shared_path.is_file())
        self.assertFalse(filter_about_path.exists())
        shared = shared_path.read_text(encoding="utf-8-sig")
        self.assertEqual(
            1,
            sum(text.count("#define FS_ABOUT_DIALOG") for text in (shared, fs_ae, cae)),
        )
        self.assertIn('#include "FsAbout.h"', fs_ae)
        self.assertIn('#include "../FsLibrary/FsAbout.h"', cae)
        self.assertIn("scriptCode,FS_ABOUT_DIALOG", "".join(fs_ae.split()))
        compact_cae = " ".join(cae.split())
        self.assertIn("scriptCode,FS_ABOUT_DIALOG", "".join(cae.split()))
        self.assertIn(
            "FS_NAME, MAJOR_VERSION, MINOR_VERSION, __DATE__, script_description",
            compact_cae,
        )
        self.assertIn('"%s, v%d.%d (%s)\\r%s"', cae)
        for text in (shared, fs_ae, cae, target):
            self.assertNotIn("FS_ABOUT_STR", text)
            self.assertNotIn("FS_CREATER", text)
        for xml in (project, filters):
            self.assertIn(r"..\..\FsLibrary\FsAbout.h", xml)
            self.assertNotIn("FilterAbout.h", xml)

    def test_incomplete_values_fallback_in_development_and_fail_publication(
        self,
    ) -> None:
        bindings = [
            {
                "role": "Param",
                "stableId": "L10N_VALUE",
                "disposition": "translated",
                "original": "Value",
            }
        ]
        catalog = {
            "schemaVersion": 1,
            "translations": {
                "en": {"Param": {"L10N_VALUE": None}},
                "zh": {"Param": {}},
            },
        }
        development = validate_effect_catalog(catalog, FS_FAMILY, bindings, publication=False)
        publication = validate_effect_catalog(catalog, FS_FAMILY, bindings, publication=True)
        self.assertTrue(all(item["severity"] != "error" for item in development))
        self.assertTrue(any(item["severity"] == "error" for item in publication))

    def test_invalid_translation_values_and_orphans_are_structural(self) -> None:
        bindings = [
            {
                "role": "Param",
                "stableId": "L10N_VALUE",
                "disposition": "translated",
                "original": "Value",
            }
        ]
        catalog = {
            "schemaVersion": 1,
            "translations": {
                "en": {
                    "Param": {
                        "L10N_VALUE": {"useSource": True, "extra": True},
                        "L10N_ORPHAN": "Orphan",
                    }
                },
                "zh": {"Param": {"L10N_VALUE": ""}},
            },
        }
        diagnostics = validate_effect_catalog(catalog, FS_FAMILY, bindings, publication=False)
        codes = diagnostic_codes(diagnostics)
        self.assertIn("AET3020", codes)
        self.assertIn("AET3023", codes)
        self.assertIn("AET3024", codes)

    def test_sync_adds_null_preserves_values_and_prunes_only_explicitly(self) -> None:
        bindings = [
            {"role": "Param", "stableId": "L10N_A", "disposition": "translated"},
            {"role": "Label", "stableId": "L10N_B", "disposition": "translated"},
            {"role": "About", "stableId": "L10N_V", "disposition": "verbatim"},
        ]
        catalog = {
            "schemaVersion": 1,
            "translations": {
                "en": {"Param": {"L10N_A": "A", "L10N_ORPHAN": "Keep until prune"}},
                "zh": {"Param": {"L10N_A": {"useSource": True}}},
            },
        }
        original = copy.deepcopy(catalog)
        preview = synchronize_effect_catalog(catalog, FS_FAMILY, bindings, prune=False)
        self.assertEqual(original, catalog)
        self.assertIsNone(preview["catalog"]["translations"]["en"]["Label"]["L10N_B"])
        self.assertIsNone(preview["catalog"]["translations"]["zh"]["Label"]["L10N_B"])
        self.assertNotIn("About", preview["catalog"]["translations"]["en"])
        self.assertIn("L10N_ORPHAN", preview["catalog"]["translations"]["en"]["Param"])
        self.assertEqual([], preview["pruned"])

        pruned = synchronize_effect_catalog(catalog, FS_FAMILY, bindings, prune=True)
        self.assertNotIn("L10N_ORPHAN", pruned["catalog"]["translations"]["en"]["Param"])
        self.assertEqual([{"locale": "en", "stableId": "L10N_ORPHAN"}], pruned["pruned"])

    def test_family_validation_rejects_duplicate_variants_and_source_locale(
        self,
    ) -> None:
        invalid = copy.deepcopy(FS_FAMILY)
        invalid["variants"][1]["textSource"]["locale"] = "ja"
        invalid["variants"][2]["id"] = "en"
        codes = diagnostic_codes(validate_family_definition(invalid))
        self.assertIn("AET2009", codes)
        self.assertIn("AET2012", codes)

    def test_legacy_baseline_matches_itself_and_detects_byte_change(self) -> None:
        baseline = {
            "schemaVersion": 1,
            "variants": ["en", "source", "zh", "source-cp936-compatible"],
            "bindings": {
                "uniqueCount": 1,
                "roleCounts": {
                    "Param": 1,
                    "Label": 0,
                    "Popup": 0,
                    "Topic": 0,
                    "About": 0,
                    "Error": 0,
                },
                "entries": [
                    {
                        "role": "Param",
                        "stableId": "L10N_VALUE",
                        "legacyHex": {
                            "en": "56616C7565",
                            "source": "56616C7565",
                            "zh": "D6B5",
                            "source-cp936-compatible": "56616C7565",
                        },
                    }
                ],
            },
            "calls": {"count": 1},
        }
        identical = compare_legacy_baseline(baseline, copy.deepcopy(baseline))
        self.assertTrue(identical["ok"])
        self.assertEqual([], identical["missing"])
        self.assertEqual([], identical["extra"])
        self.assertEqual([], identical["roleMismatches"])
        self.assertEqual([], identical["byteChanges"])

        changed = copy.deepcopy(baseline)
        changed["bindings"]["entries"][0]["legacyHex"]["zh"] = "00"
        mismatch = compare_legacy_baseline(baseline, changed)
        self.assertFalse(mismatch["ok"])
        self.assertEqual(1, len(mismatch["byteChanges"]))

    def test_legacy_migration_is_a_nonwriting_22_style_dry_run(self) -> None:
        catalog = {
            "bindings": {
                "Param": {"Value": "L10N_PARAM_VALUE"},
                "Label": {"On": "L10N_LABEL_ON"},
            },
            "translations": {"en": {}, "zh": {}},
        }
        header = """
#define L10N_PARAM_VALUE "Value"
#define L10N_LABEL_ON "On"
"""
        source = """
auto value = strings.Param(FixtureText::ParamText::Value);
auto on = strings.Label(FixtureText::LabelText::On);
auto on_again = strings.Label(FixtureText::LabelText::On);
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            header_path = root / "fixture.h"
            source_path = root / "fixture.cpp"
            header_path.write_text(header, encoding="utf-8")
            source_path.write_text(source, encoding="utf-8")
            original = source_path.read_bytes()
            report = plan_legacy_migration(
                catalog,
                [header_path, source_path],
                namespace="FixtureText",
                project_root=root,
            )
            self.assertEqual(original, source_path.read_bytes())

        self.assertEqual(2, report["legacy"]["bindingCount"])
        self.assertEqual(3, report["legacy"]["callCount"])
        self.assertEqual(report["legacy"], report["prospective"])
        self.assertEqual([], report["equivalence"]["missing"])
        self.assertEqual([], report["equivalence"]["extra"])
        self.assertEqual([], report["equivalence"]["roleMismatches"])
        self.assertIsNone(report["equivalence"]["callCountMismatch"])
        self.assertEqual([], report["diagnostics"])
        self.assertTrue(report["readyForByteComparison"])
        self.assertFalse(report["readyForBindingRemoval"])

    def test_prospective_migration_makes_legacy_english_source_explicit(self) -> None:
        catalog = {
            "bindings": {"Param": {"Value": "L10N_PARAM_VALUE"}},
            "translations": {
                "en": {},
                "zh": {"L10N_PARAM_VALUE": "值"},
            },
        }
        source = (
            '#define L10N_PARAM_VALUE "Value"\n'
            "auto value = strings.Param(FixtureText::ParamText::Value);\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_path = root / "fixture.cpp"
            source_path.write_text(source, encoding="utf-8")
            workspace = root / "prospective"
            result = materialize_legacy_migration(
                catalog,
                FS_FAMILY,
                [source_path],
                namespace="FixtureText",
                project_root=root,
                destination=workspace,
            )
            prospective_text = Path(result["catalogPath"]).read_text(encoding="utf-8")
            prospective = json.loads(prospective_text)

        self.assertEqual(
            {"useSource": True},
            prospective["translations"]["en"]["Param"]["L10N_PARAM_VALUE"],
        )
        self.assertEqual(
            [{"locale": "en", "stableId": "L10N_PARAM_VALUE"}],
            result["explicitSourceSelections"],
        )
        self.assertIn('"L10N_PARAM_VALUE": {"useSource": true}', prospective_text)

    def test_migration_plans_text_only_strings_api_cleanup(self) -> None:
        catalog = {
            "bindings": {"About": {"Description": "L10N_PLUGIN_DESC"}},
            "translations": {
                "en": {"L10N_PLUGIN_DESC": "Description"},
                "zh": {"L10N_PLUGIN_DESC": "描述"},
            },
        }
        source = r"""
#define L10N_PLUGIN_DESC "説明"
void About(PF_InData *in_data) {
    const FixtureText::Strings strings(in_data);
    const auto description = strings.About(FixtureText::AboutText::Description);
    err = ae.About(
        in_data,
        out_data,
        params,
        output,
        description.script_utf8,
        description.legacy);
}
void EffectMain(PF_InData *in_dataP) {
    switch (cmd) {
    case PF_Cmd_DO_DIALOG: {
        const FixtureText::Strings strings(in_dataP);
        strings.Options(L"F's Fixture");
        break;
    }
    }
}
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_path = root / "fixture.cpp"
            source_path.write_text(source, encoding="utf-8")
            plan = plan_legacy_migration(
                catalog,
                [source_path],
                namespace="FixtureText",
                project_root=root,
            )
            workspace = root / "prospective"
            prospective = materialize_legacy_migration(
                catalog,
                FS_FAMILY,
                [source_path],
                namespace="FixtureText",
                project_root=root,
                destination=workspace,
            )
            migrated_source = next((workspace / "sources").iterdir()).read_text(
                encoding="utf-8-sig"
            )

        self.assertEqual(1, plan["legacy"]["callCount"])
        self.assertEqual(
            {"aboutBridge": 1, "optionsCall": 1, "optionsDeclaration": 1},
            plan["apiEditCounts"],
        )
        self.assertEqual([], plan["unrewrittenLegacyCalls"])
        self.assertEqual(plan["apiEditCounts"], prospective["apiEditCounts"])
        self.assertIn("AETEXT_ABOUT(strings, L10N_PLUGIN_DESC)", migrated_source)
        self.assertIn("description);", migrated_source)
        self.assertIn('FixtureText::OpenSettings(in_dataP, L"F\'s Fixture")', migrated_source)
        self.assertNotIn("strings.Options", migrated_source)
        self.assertNotIn("description.script_utf8", migrated_source)
        self.assertNotIn("description.legacy", migrated_source)
        self.assertFalse(any(line and not line.strip() for line in migrated_source.splitlines()))

    def test_migration_rewrites_shared_about_box_representation(self) -> None:
        catalog = {
            "bindings": {"About": {"Description": "L10N_PLUGIN_DESC"}},
            "translations": {
                "en": {"L10N_PLUGIN_DESC": "Description"},
                "zh": {"L10N_PLUGIN_DESC": "描述"},
            },
        }
        source = r"""
#define L10N_PLUGIN_DESC "説明"
void About(PF_InData *in_data) {
    const FixtureText::Strings strings(in_data);
    const auto description = strings.About(FixtureText::AboutText::Description);
    AboutBox(
        display_name,
        major_version,
        minor_version,
        description.script_utf8,
        description.legacy);
}
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_path = root / "fixture.cpp"
            source_path.write_text(source, encoding="utf-8")
            plan = plan_legacy_migration(
                catalog,
                [source_path],
                namespace="FixtureText",
                project_root=root,
            )

        self.assertEqual([], plan["unrewrittenLegacyCalls"])
        self.assertEqual(1, plan["apiEditCounts"]["aboutBridge"])
        self.assertEqual("description", plan["edits"][-1]["replacement"])

    def test_apply_migration_writes_nested_review_layout_shape(self) -> None:
        catalog = {
            "bindings": {"Param": {"Value": "L10N_PARAM_VALUE"}},
            "translations": {"en": {}, "zh": {"L10N_PARAM_VALUE": "值"}},
        }
        source = (
            '#define L10N_PARAM_VALUE "Value"\n'
            "auto value = strings.Param(FixtureText::ParamText::Value);\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog_path = root / "catalog.json"
            source_path = root / "fixture.cpp"
            catalog_path.write_text(
                json.dumps(catalog, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            source_path.write_text(source, encoding="utf-8")
            plan = plan_legacy_migration(
                catalog,
                [source_path],
                namespace="FixtureText",
                project_root=root,
            )
            prospective = materialize_legacy_migration(
                catalog,
                FS_FAMILY,
                [source_path],
                namespace="FixtureText",
                project_root=root,
                destination=root / "prospective",
            )
            source_list = Path(prospective["sourceListPath"]).read_text(encoding="utf-8")
            generated = scan_sources(
                [Path(line) for line in source_list.splitlines() if line],
                project_root=root / "prospective",
            )
            equivalence = {
                "readyForBindingRemoval": True,
                "catalogSha256": hashlib.sha256(catalog_path.read_bytes()).hexdigest().upper(),
                "editedInputSha256": plan["editedInputSha256"],
                "migratedCallCount": 1,
                "apiEditCounts": plan["apiEditCounts"],
                "explicitSourceSelectionsAdded": prospective["explicitSourceSelections"],
                "reviewLayout": generated["reviewLayout"],
                "generatedBindings": generated["bindings"],
            }

            apply_legacy_migration(
                catalog_path,
                [source_path],
                namespace="FixtureText",
                project_root=root,
                equivalence_report=equivalence,
            )
            migrated_text = catalog_path.read_text(encoding="utf-8")
            migrated_catalog = json.loads(migrated_text)
            migrated_source = source_path.read_text(encoding="utf-8")

        self.assertIn("AETEXT_PARAM(strings, L10N_PARAM_VALUE)", migrated_source)
        self.assertEqual(
            {"useSource": True},
            migrated_catalog["translations"]["en"]["Param"]["L10N_PARAM_VALUE"],
        )
        self.assertEqual(
            "值",
            migrated_catalog["translations"]["zh"]["Param"]["L10N_PARAM_VALUE"],
        )
        self.assertIn('"L10N_PARAM_VALUE": {"useSource": true}', migrated_text)


if __name__ == "__main__":
    unittest.main()
