#ifndef NOMINMAX
#define NOMINMAX
#endif

#include "HostEnvironment.h"

#include "AEConfig.h"
#include "AEGP_SuiteHandler.h"

#include <Windows.h>

#include <array>
#include <cwctype>
#include <sstream>
#include <string>
#include <vector>

#pragma comment(lib, "Version.lib")

namespace FsLanguage {
namespace {

std::wstring NormalizeLanguageTag(std::wstring value)
{
	for (wchar_t &character : value) {
		character = static_cast<wchar_t>(std::towlower(character));
		if (character == L'-') {
			character = L'_';
		}
	}
	return value;
}

AeLanguage ClassifyAeLanguage(const std::wstring &language_tag)
{
	const std::wstring normalized = NormalizeLanguageTag(language_tag);
	if (normalized == L"zh_cn" || normalized == L"zh_sg") {
		return AeLanguage::SimplifiedChinese;
	}
	if (normalized.rfind(L"ja", 0) == 0) {
		return AeLanguage::Japanese;
	}
	if (normalized.rfind(L"en", 0) == 0) {
		return AeLanguage::English;
	}
	return AeLanguage::Other;
}

bool TryGetAeLanguageTag(SPBasicSuite *pica_basic, std::wstring &language_tag)
{
	if (!pica_basic) {
		return false;
	}

	try {
		AEGP_SuiteHandler suites(pica_basic);
		A_char tag[PF_APP_LANG_TAG_SIZE] = {};
		if (suites.AppSuite6()->PF_AppGetLanguage(tag)) {
			return false;
		}

		for (const unsigned char value : std::string(tag)) {
			language_tag.push_back(static_cast<wchar_t>(value));
		}
		return !language_tag.empty();
	} catch (...) {
		return false;
	}
}

bool TryGetHostVersion(std::wstring &version_text, int &major_version)
{
	std::array<wchar_t, 32768> executable_path = {};
	const DWORD path_length = GetModuleFileNameW(
		nullptr,
		executable_path.data(),
		static_cast<DWORD>(executable_path.size()));
	if (path_length == 0 || path_length >= executable_path.size()) {
		return false;
	}

	DWORD ignored = 0;
	const DWORD version_size = GetFileVersionInfoSizeW(executable_path.data(), &ignored);
	if (version_size == 0) {
		return false;
	}

	std::vector<unsigned char> version_data(version_size);
	if (!GetFileVersionInfoW(
			executable_path.data(),
			0,
			version_size,
			version_data.data())) {
		return false;
	}

	VS_FIXEDFILEINFO *fixed_info = nullptr;
	UINT fixed_info_size = 0;
	if (!VerQueryValueW(
			version_data.data(),
			L"\\",
			reinterpret_cast<void **>(&fixed_info),
			&fixed_info_size) ||
		!fixed_info || fixed_info_size < sizeof(VS_FIXEDFILEINFO)) {
		return false;
	}

	major_version = HIWORD(fixed_info->dwProductVersionMS);
	const unsigned int minor_version = LOWORD(fixed_info->dwProductVersionMS);
	const unsigned int build_version = HIWORD(fixed_info->dwProductVersionLS);
	const unsigned int revision_version = LOWORD(fixed_info->dwProductVersionLS);
	std::wostringstream version;
	version << major_version << L'.' << minor_version << L'.'
			<< build_version << L'.' << revision_version;
	version_text = version.str();
	return true;
}

WindowsCodePage ClassifyWindowsCodePage(UINT code_page)
{
	if (code_page == 932) {
		return WindowsCodePage::Japanese932;
	}
	if (code_page == 936) {
		return WindowsCodePage::SimplifiedChinese936;
	}
	return WindowsCodePage::OtherOrUnknown;
}

std::wstring WindowsLanguageName(UINT code_page)
{
	wchar_t locale_name[LOCALE_NAME_MAX_LENGTH] = {};
	wchar_t display_name[256] = {};
	std::wstring result;
	if (GetSystemDefaultLocaleName(locale_name, LOCALE_NAME_MAX_LENGTH)) {
		if (GetLocaleInfoEx(
				locale_name,
				LOCALE_SLOCALIZEDDISPLAYNAME,
				display_name,
				static_cast<int>(sizeof(display_name) / sizeof(display_name[0])))) {
			result = display_name;
		} else {
			result = locale_name;
		}
	}
	if (result.empty()) {
		result = L"unknown";
	}
	result += L" (CP" + std::to_wstring(code_page) + L')';
	return result;
}

} // namespace

HostEnvironment DetectHostEnvironment(SPBasicSuite *pica_basic)
{
	HostEnvironment result;
	if (TryGetAeLanguageTag(pica_basic, result.ae_language_tag)) {
		result.language.ae_language = ClassifyAeLanguage(result.ae_language_tag);
	}

	int major_version = 0;
	if (TryGetHostVersion(result.version_text, major_version)) {
		result.language.host_version = major_version <= 22
			? HostVersion::AtMost22
			: HostVersion::AtLeast23OrUnknown;
	}

	const UINT code_page = GetACP();
	result.language.windows_code_page = ClassifyWindowsCodePage(code_page);
	result.windows_language = WindowsLanguageName(code_page);
	return result;
}

SettingsUiLanguage DefaultSettingsUiLanguage(AeLanguage language)
{
	switch (language) {
	case AeLanguage::SimplifiedChinese: return SettingsUiLanguage::SimplifiedChinese;
	case AeLanguage::Japanese: return SettingsUiLanguage::Japanese;
	case AeLanguage::English:
	case AeLanguage::Other:
	case AeLanguage::Unavailable:
	default: return SettingsUiLanguage::English;
	}
}

} // namespace FsLanguage
