#pragma once

#include "LanguageConfig.h"
#include "LanguagePolicy.h"

#include <string>

struct SPBasicSuite;

namespace FsLanguage {

struct HostEnvironment {
	LanguageEnvironment language {
		AeLanguage::Unavailable,
		HostVersion::AtLeast23OrUnknown,
		WindowsCodePage::OtherOrUnknown
	};
	std::wstring ae_language_tag;
	std::wstring version_text;
	std::wstring windows_language;
};

HostEnvironment DetectHostEnvironment(SPBasicSuite *pica_basic);
SettingsUiLanguage DefaultSettingsUiLanguage(AeLanguage language);

} // namespace FsLanguage
