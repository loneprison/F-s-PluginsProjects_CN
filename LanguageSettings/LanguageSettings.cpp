#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0600
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif

#include "HostEnvironment.h"
#include "LanguageConfig.h"
#include "LanguagePolicy.h"
#include "LanguageSettingsResource.h"

#include "../_localization/AeText.h"
#include "../_localization/core/AeTextCatalog.h"
#include "SettingsText.generated.h"

#include "AEConfig.h"
#include "AE_GeneralPlug.h"
#include "entry.h"
#include "SPSuites.h"

#include <Windows.h>

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <mutex>
#include <sstream>
#include <string>

extern "C" DllExport AEGP_PluginInitFuncPrototype EntryPointFunc;

namespace FsLanguage {
namespace {

void ShowLanguageOptions(
	std::uint64_t owner_window,
	const wchar_t *plugin_title);

using FsLanguageSettingsText::Text;

inline constexpr std::array<Text, 5> kConfiguredLanguageText {
	Text::ModeAuto,
	Text::ModeEnglish,
	Text::ModeOriginal,
	Text::ModeSimplifiedChinese,
	Text::ModeOriginalForSimplifiedChinese
};

inline constexpr std::array<Text, 4> kSessionLanguageText {
	Text::ModeEnglish,
	Text::ModeOriginal,
	Text::ModeSimplifiedChinese,
	Text::ModeOriginalForSimplifiedChinese
};

inline constexpr std::array<Text, 19> kCompatibilityMessageText {
	Text::MessageAutoEnglishLegacyOtherWindows,
	Text::MessageAutoEnglishModern,
	Text::MessageAutoUnknownAe,
	Text::MessageAutoAeUnavailable,
	Text::MessageManualEnglish,
	Text::MessageManualJapaneseOther,
	Text::MessageManualSimplifiedChineseRecommended,
	Text::MessageManualSimplifiedChineseOriginalRisk,
	Text::MessageManualSimplifiedChineseOriginalForSimplifiedChinese,
	Text::MessageManualEnglishModernOriginalOrSimplifiedChinese,
	Text::MessageManualEnglishModernOriginalForSimplifiedChinese,
	Text::MessageManualEnglishLegacyOriginalJapanese,
	Text::MessageManualEnglishLegacyOriginalMismatch,
	Text::MessageManualEnglishLegacySimplifiedChineseOnSimplifiedChinese,
	Text::MessageManualEnglishLegacySimplifiedChineseMismatch,
	Text::MessageManualEnglishLegacyOriginalForSimplifiedChineseOnSimplifiedChinese,
	Text::MessageManualEnglishLegacyOriginalForSimplifiedChineseMismatch,
	Text::MessageManualUnknownAe,
	Text::MessageManualAeUnavailable
};

inline constexpr std::array<Text, 5> kSaveErrorText {
	Text::SaveErrorConfigDirectoryUnavailable,
	Text::SaveErrorConfigBusy,
	Text::SaveErrorDirectoryCreationFailed,
	Text::SaveErrorTemporaryFileCreationFailed,
	Text::SaveErrorSafeReplaceFailed
};

static_assert(static_cast<std::size_t>(ConfiguredLanguage::Automatic) == 0);
static_assert(static_cast<std::size_t>(ConfiguredLanguage::OriginalForSimplifiedChinese) + 1 == kConfiguredLanguageText.size());
static_assert(static_cast<std::size_t>(SessionLanguage::English) == 0);
static_assert(static_cast<std::size_t>(SessionLanguage::OriginalForSimplifiedChinese) + 1 == kSessionLanguageText.size());
static_assert(static_cast<std::size_t>(CompatibilityMessage::None) == 0);
static_assert(static_cast<std::size_t>(CompatibilityMessage::ManualAeUnavailable) == kCompatibilityMessageText.size());
static_assert(static_cast<std::size_t>(SaveError::None) == 0);
static_assert(static_cast<std::size_t>(SaveError::SafeReplaceFailed) == kSaveErrorText.size());

std::once_flag g_session_once;
HostEnvironment g_host_environment;
SessionLanguage g_session_language = SessionLanguage::Original;
RecoveryStatus g_session_recovery = RecoveryStatus::None;
SPSuiteRef g_published_suite = nullptr;

const wchar_t *UiText(SettingsUiLanguage language, Text text)
{
	const auto index = static_cast<std::uint32_t>(text);
	if (index >= FsLanguageSettingsText::kTextCount) {
		return L"";
	}

	switch (language) {
	case SettingsUiLanguage::SimplifiedChinese:
		return FsLanguageSettingsText::kSimplifiedChinese[index];
	case SettingsUiLanguage::Japanese:
		return FsLanguageSettingsText::kJapanese[index];
	case SettingsUiLanguage::English:
	default:
		return FsLanguageSettingsText::kEnglish[index];
	}
}

Text ConfiguredLanguageText(ConfiguredLanguage language)
{
	return kConfiguredLanguageText[static_cast<std::size_t>(language)];
}

Text SessionLanguageText(SessionLanguage language)
{
	return kSessionLanguageText[static_cast<std::size_t>(language)];
}

Text CompatibilityMessageText(CompatibilityMessage message)
{
	return kCompatibilityMessageText[static_cast<std::size_t>(message) - 1];
}

Text SaveErrorText(SaveError error)
{
	return kSaveErrorText[static_cast<std::size_t>(error) - 1];
}

void ReplaceAll(std::wstring &value, const std::wstring &from, const std::wstring &to)
{
	std::wstring::size_type position = 0;
	while ((position = value.find(from, position)) != std::wstring::npos) {
		value.replace(position, from.length(), to);
		position += to.length();
	}
}

std::wstring CompatibilityText(
	SettingsUiLanguage ui_language,
	ConfiguredLanguage selected_language,
	const HostEnvironment &environment)
{
	const CompatibilityMessage message = ResolveMessage(
		selected_language,
		environment.language);
	if (message == CompatibilityMessage::None) {
		return {};
	}

	std::wstring value = UiText(ui_language, CompatibilityMessageText(message));
	ReplaceAll(value, L"{windows_language}", environment.windows_language);
	ReplaceAll(
		value,
		L"{ae_language}",
		environment.ae_language_tag.empty()
			? UiText(ui_language, Text::ValueUnavailable)
			: environment.ae_language_tag);
	ReplaceAll(
		value,
		L"{selected_mode}",
		UiText(ui_language, ConfiguredLanguageText(selected_language)));
	return value;
}

void FreezeSession(SPBasicSuite *pica_basic)
{
	std::call_once(g_session_once, [pica_basic]() {
		g_host_environment = DetectHostEnvironment(pica_basic);
		const LoadedSettings settings = LoadAndRepair(
			LanguageConfigPath(),
			DefaultSettingsUiLanguage(g_host_environment.language.ae_language));
		g_session_recovery = settings.recovery;
		g_session_language = ResolveSelected(
			settings.language,
			g_host_environment.language);
	});
}

struct StableVariantId {
	const char *value;
	std::uint32_t size;
};

StableVariantId SelectedVariantId()
{
	switch (g_session_language) {
	case SessionLanguage::English: return {"en", 2};
	case SessionLanguage::SimplifiedChinese: return {"zh", 2};
	case SessionLanguage::OriginalForSimplifiedChinese:
		return {"source-cp936-compatible", 23};
	case SessionLanguage::Original:
	default: return {"source", 6};
	}
}

std::int32_t ResolveTextImpl(
	const AeText::CatalogView *catalog,
	const AeText::TextRequest *request,
	AeText::TextResult *result)
{
	if (!result) {
		return -1;
	}
	result->legacy = nullptr;
	result->utf8 = nullptr;

	if (!catalog || !request ||
		!AeText::detail::ValidCatalog(*catalog) ||
		!AeText::detail::ValidRole(request->token.role)) {
		return -1;
	}

	const StableVariantId selected_id = SelectedVariantId();
	const AeText::VariantView *variant = AeText::detail::FindVariant(
		*catalog,
		selected_id.value,
		selected_id.size);
	if (!variant) {
		variant = AeText::detail::FallbackVariant(*catalog);
	}
	const char *legacy = variant
		? AeText::detail::LegacyValue(*variant, request->token)
		: nullptr;
	if (!legacy) {
		return -1;
	}

	const bool requires_utf8 =
		request->token.role == AeText::TextRole::About ||
		request->token.role == AeText::TextRole::Error;
	const char *utf8 = requires_utf8
		? AeText::detail::Utf8Value(*variant, request->token)
		: nullptr;
	if (requires_utf8 && !utf8) {
			return -1;
	}

	result->legacy = legacy;
	result->utf8 = utf8;
	return AeText::kTextResolved;
}

SPAPI std::int32_t ResolveText(
	const AeText::CatalogView *catalog,
	const AeText::TextRequest *request,
	AeText::TextResult *result)
{
	if (result) {
		result->legacy = nullptr;
		result->utf8 = nullptr;
	}
	try {
		return ResolveTextImpl(catalog, request, result);
	} catch (...) {
		return -1;
	}
}

SPAPI void ShowOptions(
	std::uint64_t owner_window,
	const wchar_t *plugin_title)
{
	try {
		ShowLanguageOptions(owner_window, plugin_title);
	} catch (...) {
	}
}

const AeText::TextSuite1 kTextSuite {
	ResolveText,
	ShowOptions
};

int RadioId(ConfiguredLanguage language)
{
	return 1000 + static_cast<int>(language);
}

ConfiguredLanguage LanguageFromRadioId(int radio_id)
{
	const int value = radio_id - 1000;
	if (value >= static_cast<int>(ConfiguredLanguage::Automatic) &&
		value <= static_cast<int>(ConfiguredLanguage::OriginalForSimplifiedChinese)) {
		return static_cast<ConfiguredLanguage>(value);
	}
	return ConfiguredLanguage::Automatic;
}

struct DialogState {
	std::wstring plugin_title;
	std::filesystem::path config_path;
	LoadedSettings settings;
	HostEnvironment environment;
	SessionLanguage session_language = SessionLanguage::Original;
	ConfiguredLanguage selected_language = ConfiguredLanguage::Original;
	SettingsUiLanguage selected_ui_language = SettingsUiLanguage::English;
	bool read_only = false;
};

void SetControlText(HWND dialog, int id, const wchar_t *text)
{
	if (HWND control = GetDlgItem(dialog, id)) {
		SetWindowTextW(control, text);
	}
}

void RefreshDialogText(HWND dialog, const DialogState &state)
{
	const SettingsUiLanguage ui_language = state.selected_ui_language;
	SetWindowTextW(dialog, state.plugin_title.c_str());
	SetControlText(dialog, IDC_LANGUAGE_HEADING, UiText(ui_language, Text::WindowHeading));
	SetControlText(dialog, IDC_SETTINGS_UI_LANGUAGE_LABEL, UiText(ui_language, Text::WindowUiLanguage));
	SetControlText(dialog, IDC_RUNTIME_STATUS_GROUP, UiText(ui_language, Text::StatusGroup));
	SetControlText(dialog, IDC_COMPATIBILITY_GROUP, UiText(ui_language, Text::CompatibilityGroup));
	SetControlText(dialog, IDC_PLUGIN_LANGUAGE_GROUP, UiText(ui_language, Text::PluginLanguageGroup));
	SetControlText(dialog, IDOK, UiText(ui_language, Text::ButtonSave));
	SetControlText(
		dialog,
		IDCANCEL,
		UiText(ui_language, state.read_only ? Text::ButtonBack : Text::ButtonCancel));

	for (int value = static_cast<int>(ConfiguredLanguage::Automatic);
		 value <= static_cast<int>(ConfiguredLanguage::OriginalForSimplifiedChinese);
		 ++value) {
		const auto language = static_cast<ConfiguredLanguage>(value);
		SetControlText(
			dialog,
			RadioId(language),
			UiText(ui_language, ConfiguredLanguageText(language)));
	}

	const SessionLanguage next_language = ResolveSelected(
		state.selected_language,
		state.environment.language);
	std::wostringstream status;
	status << UiText(ui_language, Text::StatusAeLanguage) << L": "
		   << (state.environment.ae_language_tag.empty()
				? UiText(ui_language, Text::ValueUnavailable)
				: state.environment.ae_language_tag)
		   << L"\r\n"
		   << UiText(ui_language, Text::StatusAeVersion) << L": "
		   << (state.environment.version_text.empty()
				? UiText(ui_language, Text::ValueUnknown)
				: state.environment.version_text)
		   << L"\r\n"
		   << UiText(ui_language, Text::StatusWindowsLanguage) << L": "
		   << state.environment.windows_language
		   << L"\r\n"
		   << UiText(ui_language, Text::StatusCurrentLanguage) << L": "
		   << UiText(ui_language, SessionLanguageText(state.session_language))
		   << L"\r\n"
		   << UiText(ui_language, Text::StatusNextLanguage) << L": "
		   << (state.read_only
				? L"-"
				: UiText(ui_language, SessionLanguageText(next_language)));
	if (!state.read_only && next_language != state.session_language) {
		status << L"\r\n"
			   << UiText(
					ui_language,
					state.selected_language == state.settings.language
						? Text::StatusRestart
						: Text::StatusSaveAndRestart);
	}
	if (state.read_only) {
		status << L"\r\n" << UiText(ui_language, Text::StatusInvalidConfig);
	} else if (!state.settings.file_exists) {
		status << L"\r\n" << UiText(ui_language, Text::StatusNoConfig);
	} else if (state.settings.version_mismatch) {
		status << L"\r\n" << UiText(ui_language, Text::StatusConfigVersionCompatibility);
		if (state.settings.used_field_defaults) {
			status << L"\r\n" << UiText(ui_language, Text::StatusConfigVersionDefaults);
		}
	} else if (state.settings.recovery == RecoveryStatus::DefaultsRepaired) {
		status << L"\r\n" << UiText(ui_language, Text::StatusConfigRepaired);
	} else if (state.settings.recovery == RecoveryStatus::FieldsRepaired) {
		status << L"\r\n" << UiText(ui_language, Text::StatusConfigFieldsRepaired);
	} else if (state.settings.recovery == RecoveryStatus::BackupFailed) {
		status << L"\r\n" << UiText(ui_language, Text::StatusConfigBackupFailed);
	} else if (state.settings.recovery == RecoveryStatus::RepairWriteFailed) {
		status << L"\r\n" << UiText(ui_language, Text::StatusConfigRepairWriteFailed);
	} else if (!state.settings.valid) {
		status << L"\r\n" << UiText(ui_language, Text::StatusInvalidConfig);
	}
	SetControlText(dialog, IDC_RUNTIME_STATUS, status.str().c_str());

	const std::wstring compatibility = CompatibilityText(
		ui_language,
		state.selected_language,
		state.environment);
	SetControlText(dialog, IDC_COMPATIBILITY_MESSAGE, compatibility.c_str());
}

bool InitializeDialogControls(HWND dialog, DialogState &state)
{
	HWND ui_language_combo = GetDlgItem(dialog, IDC_SETTINGS_UI_LANGUAGE);
	if (!ui_language_combo) {
		return false;
	}

	constexpr const wchar_t *kUiLanguageNames[] = {
		L"English",
		L"\u7B80\u4F53\u4E2D\u6587",
		L"\u65E5\u672C\u8A9E"
	};
	for (const wchar_t *name : kUiLanguageNames) {
		SendMessageW(
			ui_language_combo,
			CB_ADDSTRING,
			0,
			reinterpret_cast<LPARAM>(name));
	}
	SendMessageW(
		ui_language_combo,
		CB_SETCURSEL,
		static_cast<WPARAM>(state.selected_ui_language),
		0);

	CheckRadioButton(
		dialog,
		RadioId(ConfiguredLanguage::Automatic),
		RadioId(ConfiguredLanguage::OriginalForSimplifiedChinese),
		RadioId(state.selected_language));

	const BOOL settings_enabled = state.read_only ? FALSE : TRUE;
	for (int value = static_cast<int>(ConfiguredLanguage::Automatic);
		 value <= static_cast<int>(ConfiguredLanguage::OriginalForSimplifiedChinese);
		 ++value) {
		if (HWND control = GetDlgItem(
				dialog,
				RadioId(static_cast<ConfiguredLanguage>(value)))) {
			EnableWindow(control, settings_enabled);
		}
	}
	if (HWND save_button = GetDlgItem(dialog, IDOK)) {
		EnableWindow(save_button, settings_enabled);
	}
	RefreshDialogText(dialog, state);
	return true;
}

HMODULE CurrentModule()
{
	HMODULE module = nullptr;
	GetModuleHandleExW(
		GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
			GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
		reinterpret_cast<LPCWSTR>(&ShowLanguageOptions),
		&module);
	return module;
}

INT_PTR LanguageDialogProcImpl(
	HWND dialog,
	UINT message,
	WPARAM w_param,
	LPARAM l_param)
{
	DialogState *state = reinterpret_cast<DialogState *>(
		GetWindowLongPtrW(dialog, DWLP_USER));

	switch (message) {
	case WM_INITDIALOG:
		state = reinterpret_cast<DialogState *>(l_param);
		SetWindowLongPtrW(dialog, DWLP_USER, reinterpret_cast<LONG_PTR>(state));
		if (!state || !InitializeDialogControls(dialog, *state)) {
			EndDialog(dialog, IDCANCEL);
		}
		return TRUE;

	case WM_COMMAND:
		if (!state) {
			return FALSE;
		}
		if (state->read_only &&
			LOWORD(w_param) != IDCANCEL &&
			!(LOWORD(w_param) == IDC_SETTINGS_UI_LANGUAGE &&
			  HIWORD(w_param) == CBN_SELCHANGE)) {
			return TRUE;
		}

		if (LOWORD(w_param) == IDC_SETTINGS_UI_LANGUAGE &&
			HIWORD(w_param) == CBN_SELCHANGE) {
			const LRESULT selection = SendDlgItemMessageW(
				dialog,
				IDC_SETTINGS_UI_LANGUAGE,
				CB_GETCURSEL,
				0,
				0);
			if (selection >= static_cast<LRESULT>(SettingsUiLanguage::English) &&
				selection <= static_cast<LRESULT>(SettingsUiLanguage::Japanese)) {
				state->selected_ui_language = static_cast<SettingsUiLanguage>(selection);
				RefreshDialogText(dialog, *state);
			}
			return TRUE;
		}

		if (LOWORD(w_param) >= RadioId(ConfiguredLanguage::Automatic) &&
			LOWORD(w_param) <= RadioId(ConfiguredLanguage::OriginalForSimplifiedChinese) &&
			HIWORD(w_param) == BN_CLICKED) {
			state->selected_language = LanguageFromRadioId(LOWORD(w_param));
			RefreshDialogText(dialog, *state);
			return TRUE;
		}

		if (LOWORD(w_param) == IDOK) {
			const SaveError error = SaveLanguageSettings(
				state->config_path,
				state->selected_language,
				state->selected_ui_language);
			if (error == SaveError::None) {
				EndDialog(dialog, IDOK);
			} else {
				MessageBoxW(
					dialog,
					UiText(state->selected_ui_language, SaveErrorText(error)),
					state->plugin_title.c_str(),
					MB_OK | MB_ICONERROR);
			}
			return TRUE;
		}

		if (LOWORD(w_param) == IDCANCEL) {
			EndDialog(dialog, IDCANCEL);
			return TRUE;
		}
		break;

	case WM_CLOSE:
		EndDialog(dialog, IDCANCEL);
		return TRUE;
	}

	return FALSE;
}

INT_PTR CALLBACK LanguageDialogProc(
	HWND dialog,
	UINT message,
	WPARAM w_param,
	LPARAM l_param)
{
	try {
		return LanguageDialogProcImpl(dialog, message, w_param, l_param);
	} catch (...) {
		EndDialog(dialog, IDCANCEL);
		return FALSE;
	}
}

class SuitesSuiteLease final {
public:
	explicit SuitesSuiteLease(SPBasicSuite *pica_basic) noexcept
		: pica_basic_(pica_basic)
	{
		if (pica_basic_ && pica_basic_->AcquireSuite) {
			acquire_error_ = pica_basic_->AcquireSuite(
				kSPSuitesSuite,
				kSPSuitesSuiteVersion,
				&suite_pointer_);
		}
	}

	~SuitesSuiteLease() noexcept
	{
		(void)Release();
	}

	SuitesSuiteLease(const SuitesSuiteLease &) = delete;
	SuitesSuiteLease &operator=(const SuitesSuiteLease &) = delete;

	SPErr Error() const noexcept { return acquire_error_; }
	const SPSuitesSuite *Get() const noexcept
	{
		return acquire_error_ == 0
			? static_cast<const SPSuitesSuite *>(suite_pointer_)
			: nullptr;
	}

	SPErr Release() noexcept
	{
		if (!suite_pointer_) {
			return 0;
		}
		const SPErr error = pica_basic_ && pica_basic_->ReleaseSuite
			? pica_basic_->ReleaseSuite(kSPSuitesSuite, kSPSuitesSuiteVersion)
			: A_Err_GENERIC;
		suite_pointer_ = nullptr;
		return error;
	}

private:
	SPBasicSuite *pica_basic_ = nullptr;
	const void *suite_pointer_ = nullptr;
	SPErr acquire_error_ = A_Err_GENERIC;
};

A_Err PublishTextSuite(SPBasicSuite *pica_basic)
{
	if (!pica_basic) {
		return A_Err_GENERIC;
	}

	SuitesSuiteLease lease(pica_basic);
	const SPSuitesSuite *suites = lease.Get();
	if (!suites) {
		return static_cast<A_Err>(lease.Error() ? lease.Error() : A_Err_GENERIC);
	}

	const SPErr add_error = suites->AddSuite(
		kSPRuntimeSuiteList,
		nullptr,
		FsLanguageSettingsText::kRuntimeSuiteName,
		FsLanguageSettingsText::kRuntimeSuiteVersion,
		FsLanguageSettingsText::kRuntimeSuiteInternalVersion,
		&kTextSuite,
		&g_published_suite);
	const SPErr release_error = lease.Release();
	return static_cast<A_Err>(add_error ? add_error : release_error);
}

void ShowLanguageOptions(
	std::uint64_t owner_window,
	const wchar_t *plugin_title)
{
	FreezeSession(nullptr);

	DialogState state;
	state.plugin_title = plugin_title ? plugin_title : L"F's Plugins";
	state.config_path = LanguageConfigPath();
	state.environment = g_host_environment;
	state.settings = LoadAndRepair(
		state.config_path,
		DefaultSettingsUiLanguage(state.environment.language.ae_language));
	state.read_only =
		!state.settings.valid &&
		state.settings.recovery == RecoveryStatus::None;
	if (!state.read_only && state.settings.recovery == RecoveryStatus::None) {
		state.settings.recovery = g_session_recovery;
	}
	state.session_language = g_session_language;
	state.selected_language = state.settings.language;
	state.selected_ui_language = state.settings.ui_language;

	DialogBoxParamW(
		CurrentModule(),
		MAKEINTRESOURCEW(IDD_FS_LANGUAGE_SETTINGS),
		reinterpret_cast<HWND>(static_cast<std::uintptr_t>(owner_window)),
		LanguageDialogProc,
		reinterpret_cast<LPARAM>(&state));
}

} // namespace
} // namespace FsLanguage

A_Err EntryPointFunc(
	SPBasicSuite *pica_basicP,
	A_long major_versionL,
	A_long minor_versionL,
	AEGP_PluginID aegp_plugin_id,
	AEGP_GlobalRefcon *global_refconP)
{
	(void)major_versionL;
	(void)minor_versionL;
	(void)aegp_plugin_id;
	(void)global_refconP;

	try {
		FsLanguage::FreezeSession(pica_basicP);
		return FsLanguage::PublishTextSuite(pica_basicP);
	} catch (...) {
		return A_Err_GENERIC;
	}
}
