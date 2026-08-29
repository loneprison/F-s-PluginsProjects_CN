from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

import pytest
from playwright.sync_api import Page, expect

SERVER = Path(__file__).with_name("review_fixture_server.py")


def _write_fixture(root: Path, *, interactions: bool = False) -> Path:
    catalog = root / "_localization" / "catalog" / "(Templates)" / "Fixture.json"
    family_root = root / "_localization" / "families" / "fs"
    family = family_root / "generation.json"
    workflow = family_root / "review-workflow.json"
    catalog.parent.mkdir(parents=True)
    family.parent.mkdir(parents=True)
    translations: dict[str, dict[str, dict[str, object]]] = {
        "en": {"Param": {"L10N_VALUE": {"useSource": True}}},
        "zh": {"Param": {"L10N_VALUE": "值"}},
    }
    source_text = '#define L10N_VALUE "Value"\nauto value = AETEXT_PARAM(strings, L10N_VALUE);\n'
    if interactions:
        translations["en"].update(
            {
                "Popup": {"L10N_MENU": {"useSource": True}},
                "About": {"L10N_ABOUT": {"useSource": True}},
            }
        )
        translations["zh"].update(
            {
                "Popup": {"L10N_MENU": "一|(-|二||三"},
                "About": {"L10N_ABOUT": "关于这个效果"},
            }
        )
        source_text += (
            '#define L10N_MENU "One|(-|Two||Three"\n'
            '#define L10N_ABOUT "About this effect"\n'
            "auto menu = AETEXT_POPUP(strings, L10N_MENU);\n"
            "auto about = AETEXT_ABOUT(strings, L10N_ABOUT);\n"
        )
    catalog.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "translations": translations,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    family.write_text(
        json.dumps(
            {
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
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    workflow.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "enabled": True,
                "stages": [
                    {
                        "id": "needs-review",
                        "label": "待核对",
                        "color": "orange",
                        "enabled": True,
                    },
                    {
                        "id": "reviewed",
                        "label": "已校对",
                        "color": "green",
                        "enabled": True,
                    },
                ],
                "completedStageId": "reviewed",
                "defaults": {"manualEdit": "needs-review", "pretranslation": None},
                "sourceChange": {"reviewed": "needs-review"},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "Fixture.cpp").write_text(source_text, encoding="utf-8")
    (root / "Fixture.vcxproj").write_text("<Project />", encoding="utf-8")
    (root / "Legacy.vcxproj").write_text("<Project />", encoding="utf-8")
    legacy = root / "_localization" / "catalog" / "NF's Plugins-Filter" / "Legacy.json"
    legacy.parent.mkdir(parents=True)
    legacy.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "bindings": {"Param": {"Value": "L10N_VALUE"}},
                "translations": {"en": {"Value": "Value"}, "zh": {"Value": "值"}},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return catalog


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


@contextmanager
def _running_review_server(root: Path, catalog: Path) -> Iterator[tuple[str, Path]]:
    port = _free_port()
    child_environment = os.environ.copy()
    child_environment.pop("NICEGUI_SCREEN_TEST_PORT", None)
    child_environment.pop("PYTEST_CURRENT_TEST", None)
    process = subprocess.Popen(
        [sys.executable, str(SERVER), str(root), str(port)],
        env=child_environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )
    assert process.stdout is not None
    line = process.stdout.readline().strip()
    assert line.startswith("AeText review: http://127.0.0.1:"), line
    url = line.removeprefix("AeText review: ")
    deadline = time.monotonic() + 10
    while True:
        try:
            with urlopen(url, timeout=1) as response:
                assert response.status == 200
            break
        except URLError as error:
            if process.poll() is not None:
                raise AssertionError(process.stdout.read()) from error
            if time.monotonic() >= deadline:
                raise TimeoutError(f"review server did not become ready: {url}") from error
            time.sleep(0.1)
    try:
        yield url, catalog
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


@pytest.fixture
def review_server(tmp_path: Path) -> Iterator[tuple[str, Path]]:
    catalog = _write_fixture(tmp_path)
    with _running_review_server(tmp_path, catalog) as server:
        yield server


@pytest.fixture
def interaction_review_server(tmp_path: Path) -> Iterator[tuple[str, Path]]:
    catalog = _write_fixture(tmp_path, interactions=True)
    with _running_review_server(tmp_path, catalog) as server:
        yield server


def _edit_translation(page: Page, value: str) -> None:
    cell = page.locator('.ag-center-cols-container .ag-row [col-id="translation"]').first
    editor = cell.locator(".aetext-translation-input")
    editor.fill(value)


def _scan_fixture(page: Page) -> None:
    expect(page.get_by_text("尚未建立源码索引。")).to_be_visible()
    page.get_by_role("button", name="扫描当前插件").click()
    expect(page.get_by_text("Fixture", exact=True)).to_be_visible()
    expect(page.locator(".ag-center-cols-container .ag-row")).to_have_count(1)


def _section(page: Page, label: str):
    index = {"参数名称": 0, "下拉选项": 1, "About": 2}[label]
    return page.locator(".nicegui-aggrid").nth(index)


@pytest.mark.e2e
def test_web_review_saves_only_current_locale(page: Page, review_server: tuple[str, Path]) -> None:
    url, catalog = review_server
    requests: list[str] = []
    page.on("request", lambda request: requests.append(request.url))

    page.goto(url)
    _scan_fixture(page)
    _edit_translation(page, "新值")
    page.get_by_role("button", name="保存当前语言").click()
    expect(page.get_by_text("已保存当前插件的当前语言")).to_be_visible()

    document = json.loads(catalog.read_text(encoding="utf-8"))
    assert document["translations"]["en"] == {"Param": {"L10N_VALUE": {"useSource": True}}}
    assert document["translations"]["zh"] == {"Param": {"L10N_VALUE": "新值"}}
    assert document["workflow"]["zh"] == {"Param": {"L10N_VALUE": "needs-review"}}
    assert {urlsplit(request).hostname for request in requests} == {"127.0.0.1"}
    parsed = urlsplit(url)
    assert page.request.get(f"{parsed.scheme}://{parsed.netloc}/").status == 404


@pytest.mark.e2e
def test_web_workspace_uses_project_tree_navigation(
    page: Page,
    review_server: tuple[str, Path],
) -> None:
    url, _ = review_server
    page.goto(url)
    tree = page.locator(".q-tree")

    expect(page.get_by_text("AeText", exact=True)).to_be_visible()
    expect(tree.get_by_text("正式插件", exact=False)).to_be_visible()
    expect(tree.get_by_text("Filter", exact=False)).to_be_visible()
    expect(tree.get_by_text("Legacy", exact=False)).to_be_visible()
    expect(tree.get_by_text("模板", exact=False)).to_be_visible()
    expect(tree.get_by_text("Fixture", exact=False)).to_be_visible()
    expect(page.get_by_text("工程总数")).not_to_be_visible()

    page.get_by_label("搜索插件名").fill("Fixture")
    expect(tree.get_by_text("模板", exact=False)).to_be_visible()
    expect(tree.get_by_text("Fixture", exact=False)).to_be_visible()
    expect(tree.get_by_text("Legacy", exact=False)).not_to_be_visible()


@pytest.mark.e2e
def test_web_locale_switch_updates_existing_page(
    page: Page, review_server: tuple[str, Path]
) -> None:
    url, _ = review_server
    page.goto(url)
    _scan_fixture(page)
    translation = page.locator('.ag-center-cols-container .ag-row [col-id="translation"]').first
    expect(translation.locator("input")).to_have_value("值")

    page.get_by_label("语言").click()
    page.get_by_text("en", exact=True).last.click()
    expect(page.get_by_text("使用原文 1", exact=True)).to_be_visible()

    page.get_by_label("语言").click()
    page.get_by_text("zh", exact=True).last.click()
    expect(translation.locator("input")).to_have_value("值")


@pytest.mark.e2e
def test_web_review_refuses_stale_page(page: Page, review_server: tuple[str, Path]) -> None:
    url, catalog = review_server
    page.goto(url)
    _scan_fixture(page)
    external = json.loads(catalog.read_text(encoding="utf-8"))
    external["translations"]["zh"]["Param"]["L10N_VALUE"] = "外部修改"
    catalog.write_text(
        json.dumps(external, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    _edit_translation(page, "旧页面")
    page.get_by_role("button", name="保存当前语言").click()
    expect(page.get_by_text("保存失败，磁盘内容未覆盖")).to_be_visible()  # noqa: RUF001

    document = json.loads(catalog.read_text(encoding="utf-8"))
    assert document["translations"]["zh"]["Param"]["L10N_VALUE"] == "外部修改"


@pytest.mark.e2e
def test_web_batches_workflow_stage_and_can_hide_workflow_without_data_loss(
    page: Page,
    review_server: tuple[str, Path],
) -> None:
    url, catalog = review_server
    page.goto(url)
    _scan_fixture(page)

    missing_chip = page.locator(".q-chip").filter(has_text="待翻译")
    missing_chip.click()
    expect(page.locator(".ag-center-cols-container .ag-row")).to_have_count(0)
    missing_chip.click()
    expect(page.locator(".ag-center-cols-container .ag-row")).to_have_count(1)

    page.locator('.ag-center-cols-container .ag-row input[type="checkbox"]').first.click()
    page.get_by_label("批量设置阶段").click()
    page.get_by_text("已校对", exact=True).last.click()
    page.get_by_role("button", name="应用到所选").click()
    workflow_cell = page.locator(
        '.ag-center-cols-container .ag-row [col-id="workflow_stage"]'
    ).first
    expect(workflow_cell.locator("select")).to_have_value("reviewed")
    page.get_by_role("button", name="保存当前语言").click()
    expect(page.get_by_text("已保存当前插件的当前语言")).to_be_visible()

    page.get_by_role("button", name="工作流设置").click()
    workflow_switch = page.get_by_role("switch", name="启用审校流程")
    expect(workflow_switch).to_be_checked()
    workflow_switch.click()
    page.get_by_role("button", name="保存设置").click()
    expect(page.get_by_role("columnheader", name="审校阶段")).not_to_be_visible()

    document = json.loads(catalog.read_text(encoding="utf-8"))
    assert document["workflow"]["zh"] == {"Param": {"L10N_VALUE": "reviewed"}}


@pytest.mark.e2e
def test_web_applies_stage_to_all_without_eager_save_or_unrelated_refresh(
    page: Page,
    interaction_review_server: tuple[str, Path],
) -> None:
    url, catalog = interaction_review_server
    page.goto(url)
    page.get_by_role("button", name="扫描当前插件").click()

    expect(page.get_by_role("button", name="应用到全部 3 项")).to_be_visible()
    expect(page.get_by_role("button", name="标记已校对并下一条")).not_to_be_visible()

    param = _section(page, "参数名称")
    popup = _section(page, "下拉选项")
    popup_button = popup.get_by_role("button", name="编辑下拉项…（5 项）")  # noqa: RUF001
    popup_button.evaluate("element => { window.aetextUnchangedPopup = element; }")

    param.locator(
        '.ag-center-cols-container [col-id="ag-Grid-SelectionColumn"] input[type="checkbox"]'
    ).click()
    page.get_by_label("批量设置阶段").click()
    page.get_by_text("已校对", exact=True).last.click()
    page.get_by_role("button", name="应用到所选").click()
    assert popup_button.evaluate("element => element === window.aetextUnchangedPopup")

    reviewed_chip = page.locator(".q-chip").filter(has_text="已校对").first
    reviewed_chip.click()
    expect(param.locator(".ag-center-cols-container .ag-row")).to_have_count(1)
    expect(popup.locator(".ag-center-cols-container .ag-row")).to_have_count(0)

    about_header = (
        page.locator(".q-item__label")
        .filter(has_text="About 1 / 1")
        .first.locator("xpath=ancestor::*[@role='button'][1]")
    )
    about_header.click()
    expect(about_header).to_have_attribute("aria-expanded", "false")

    page.get_by_label("批量设置阶段").click()
    page.get_by_text("待核对", exact=True).last.click()
    catalog_before = catalog.read_bytes()
    page.get_by_role("button", name="应用到全部 3 项").click()
    confirmation = page.get_by_role("dialog")
    expect(confirmation.get_by_text("当前插件、当前语言的全部 3 项")).to_be_visible()
    confirmation.get_by_role("button", name="确认应用到全部").click()
    expect(param.locator(".ag-center-cols-container .ag-row")).to_have_count(0)
    assert catalog.read_bytes() == catalog_before

    tree = page.locator(".q-tree")
    tree.evaluate("element => { window.aetextTreeBeforeSave = element; }")
    page.get_by_role("button", name="保存当前语言").click()
    expect(page.get_by_text("已保存当前插件的当前语言", exact=True)).to_be_visible()
    assert tree.evaluate("element => element === window.aetextTreeBeforeSave")

    document = json.loads(catalog.read_text(encoding="utf-8"))
    assert document["workflow"]["zh"] == {
        "Param": {"L10N_VALUE": "needs-review"},
        "Popup": {"L10N_MENU": "needs-review"},
        "About": {"L10N_ABOUT": "needs-review"},
    }


@pytest.mark.e2e
def test_translation_workbench_uses_specialized_controls_and_preserves_context(
    page: Page,
    interaction_review_server: tuple[str, Path],
) -> None:
    url, catalog = interaction_review_server
    page.context.grant_permissions(
        ["clipboard-read", "clipboard-write"],
        origin=f"{urlsplit(url).scheme}://{urlsplit(url).netloc}",
    )
    page.goto(url)
    page.get_by_role("button", name="扫描当前插件").click()
    expect(page.get_by_text("有效 3", exact=True)).to_be_visible()

    param = _section(page, "参数名称")
    popup = _section(page, "下拉选项")
    about = _section(page, "About")
    expect(param.locator(".aetext-translation-input")).to_have_value("值")
    expect(about.locator("textarea.aetext-translation-input")).to_have_value("关于这个效果")

    param.locator(".aetext-original-wrap").dblclick()
    expect(page.get_by_text("已复制原文", exact=True)).to_be_visible()
    assert page.evaluate("navigator.clipboard.readText()") == "Value"

    use_source = param.locator('[col-id="use_source"] input[type="checkbox"]')
    use_source.click()
    expect(param.locator(".aetext-translation-input")).to_be_disabled()
    use_source.click()
    expect(param.locator(".aetext-translation-input")).to_be_enabled()
    param.locator(".aetext-translation-input").fill("新值")
    param.locator(".aetext-translation-input").blur()
    expect(page.get_by_role("button", name=re.compile("参数名称.*未保存"))).to_be_visible()

    popup.locator(".aetext-stage-select").select_option("reviewed")
    expect(popup.locator(".aetext-stage-select")).to_have_value("reviewed")
    expect(page.get_by_role("button", name=re.compile("下拉选项.*未保存"))).to_be_visible()

    popup.get_by_role("button", name="编辑下拉项…（5 项）").click()  # noqa: RUF001
    dialog = page.get_by_role("dialog")
    expect(
        dialog.get_by_text("—— 分隔符（结构只读）——", exact=True)  # noqa: RUF001
    ).to_be_visible()
    expect(dialog.get_by_text("空项（结构只读）", exact=True)).to_be_visible()  # noqa: RUF001
    popup_inputs = dialog.locator("input")
    expect(popup_inputs).to_have_count(3)
    popup_inputs.nth(0).fill("(-")
    expect(dialog.get_by_text("第 1 项的分隔符结构与原文不一致", exact=True)).to_be_visible()
    expect(dialog.get_by_role("button", name="应用到译文")).to_be_disabled()
    popup_inputs.nth(0).fill("壹")
    popup_inputs.nth(1).fill("贰")
    popup_inputs.nth(2).fill("叁")
    expect(dialog.get_by_text("结构有效", exact=True)).to_be_visible()
    dialog.get_by_role("button", name="应用到译文").click()
    expect(dialog).not_to_be_visible()

    about.locator("textarea.aetext-translation-input").fill("😀")
    assert page.evaluate("window.aetextDrafts.L10N_ABOUT") == "😀"
    page.get_by_role("button", name="保存当前语言").click()
    expect(
        page.get_by_text("存在结构或编码错误，未保存", exact=True)  # noqa: RUF001
    ).to_be_visible()
    expect(about.locator(".aetext-row-validation")).to_contain_text("not encodable")
    about.locator("textarea.aetext-translation-input").fill("关于这个效果")

    valid_chip = page.locator(".q-chip").filter(has_text="有效 3")
    valid_chip.click()
    popup.locator(
        '.ag-center-cols-container [col-id="ag-Grid-SelectionColumn"] input[type="checkbox"]'
    ).click()
    about_header = (
        page.locator(".q-item__label")
        .filter(has_text="About 1 / 1")
        .first.locator("xpath=ancestor::*[@role='button'][1]")
    )
    about_header.click()
    expect(about_header).to_have_attribute("aria-expanded", "false")

    param_input = param.locator(".aetext-translation-input")
    tree = page.locator(".q-tree")
    param_input.evaluate("element => { window.aetextInputBeforeSave = element; }")
    tree.evaluate("element => { window.aetextTreeBeforeSave = element; }")
    page.get_by_role("button", name="保存当前语言").click()
    expect(page.get_by_text("已保存当前插件的当前语言", exact=True)).to_be_visible()
    assert param_input.evaluate("element => element === window.aetextInputBeforeSave")
    assert tree.evaluate("element => element === window.aetextTreeBeforeSave")
    expect(about_header).to_have_attribute("aria-expanded", "false")
    expect(valid_chip).to_have_class(re.compile("q-chip--selected"))
    expect(
        popup.locator(
            '.ag-center-cols-container [col-id="ag-Grid-SelectionColumn"] input[type="checkbox"]'
        )
    ).to_be_checked()

    document = json.loads(catalog.read_text(encoding="utf-8"))
    assert document["translations"]["zh"]["Param"]["L10N_VALUE"] == "新值"
    assert document["translations"]["zh"]["Popup"]["L10N_MENU"] == "壹|(-|贰||叁"
    assert document["workflow"]["zh"]["Popup"]["L10N_MENU"] == "reviewed"


@pytest.mark.e2e
def test_unsaved_context_replacements_require_explicit_choice(
    page: Page,
    review_server: tuple[str, Path],
) -> None:
    url, catalog = review_server
    page.goto(url)
    _scan_fixture(page)
    tree = page.locator(".q-tree")

    _edit_translation(page, "保留的草稿")
    tree.get_by_text("Legacy", exact=False).click()
    unsaved = page.get_by_role("dialog").filter(has_text="有未保存的更改")
    expect(unsaved).to_be_visible()
    unsaved.get_by_role("button", name="取消").click()
    expect(page.locator(".aetext-translation-input").first).to_have_value("保留的草稿")

    page.get_by_label("语言").click()
    page.get_by_text("en", exact=True).last.click()
    expect(unsaved).to_be_visible()
    unsaved.get_by_role("button", name="放弃并继续").click()
    expect(page.get_by_label("语言")).to_have_value("en")
    expect(page.get_by_text("使用原文 1", exact=True)).to_be_visible()

    page.get_by_label("语言").click()
    page.get_by_text("zh", exact=True).last.click()
    _edit_translation(page, "保存后扫描")
    page.get_by_role("button", name="扫描").click()
    page.get_by_text("扫描当前插件源码", exact=True).click()
    expect(unsaved).to_be_visible()
    unsaved.get_by_role("button", name="保存并继续").click()
    expect(page.get_by_text("已保存当前插件的当前语言", exact=True)).to_be_visible()
    expect(page.get_by_text("源码索引已更新", exact=True)).to_be_visible()
    expect(page.locator(".aetext-translation-input").first).to_have_value("保存后扫描")
    assert json.loads(catalog.read_text(encoding="utf-8"))["translations"]["zh"]["Param"] == {
        "L10N_VALUE": "保存后扫描"
    }

    _edit_translation(page, "重新读取前的草稿")
    page.get_by_role("button", name="扫描").click()
    page.get_by_text("重新读取翻译文件", exact=True).click()
    expect(unsaved).to_be_visible()
    unsaved.get_by_role("button", name="取消").click()
    expect(page.locator(".aetext-translation-input").first).to_have_value("重新读取前的草稿")

    page.get_by_role("button", name="工作流设置").click()
    expect(unsaved).to_be_visible()
    unsaved.get_by_role("button", name="放弃并继续").click()
    workflow = page.get_by_role("dialog").filter(has_text="F's 审校工作流设置")
    expect(workflow).to_be_visible()
    workflow.get_by_role("button", name="取消").click()

    _edit_translation(page, "扫描全部前的草稿")
    page.get_by_role("button", name="扫描").click()
    page.get_by_text("扫描所有插件源码", exact=True).click()
    expect(unsaved).to_be_visible()
    unsaved.get_by_role("button", name="取消").click()
    expect(page.locator(".aetext-translation-input").first).to_have_value("扫描全部前的草稿")
