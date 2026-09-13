#pragma once

#include <cstdint>

namespace FsLanguage {

enum class ConfiguredLanguage : std::uint8_t {
	Automatic,
	English,
	Original,
	SimplifiedChinese,
	OriginalForSimplifiedChinese
};

enum class SessionLanguage : std::uint8_t {
	English,
	Original,
	SimplifiedChinese,
	OriginalForSimplifiedChinese
};

enum class AeLanguage : std::uint8_t {
	SimplifiedChinese,
	Japanese,
	English,
	Other,
	Unavailable
};

enum class HostVersion : std::uint8_t {
	AtMost22,
	AtLeast23OrUnknown
};

enum class WindowsCodePage : std::uint8_t {
	Japanese932,
	SimplifiedChinese936,
	OtherOrUnknown
};

enum class CompatibilityMessage : std::uint8_t {
	None,
	Incompatible
};

struct LanguageEnvironment {
	AeLanguage ae_language;
	HostVersion host_version;
	WindowsCodePage windows_code_page;
};

constexpr SessionLanguage ResolveAutomatic(const LanguageEnvironment &environment)
{
	if (environment.host_version == HostVersion::AtMost22) {
		switch (environment.windows_code_page) {
		case WindowsCodePage::SimplifiedChinese936:
			return SessionLanguage::SimplifiedChinese;
		case WindowsCodePage::Japanese932:
			return SessionLanguage::Original;
		case WindowsCodePage::OtherOrUnknown:
		default:
			return SessionLanguage::English;
		}
	}

	switch (environment.ae_language) {
	case AeLanguage::SimplifiedChinese:
		return SessionLanguage::SimplifiedChinese;
	case AeLanguage::Japanese:
		return SessionLanguage::Original;
	case AeLanguage::English:
	case AeLanguage::Other:
	case AeLanguage::Unavailable:
	default:
		return SessionLanguage::English;
	}
}

constexpr SessionLanguage ResolveSelected(
	ConfiguredLanguage selected,
	const LanguageEnvironment &environment)
{
	switch (selected) {
	case ConfiguredLanguage::Automatic:
		return ResolveAutomatic(environment);
	case ConfiguredLanguage::English:
		return SessionLanguage::English;
	case ConfiguredLanguage::SimplifiedChinese:
		return SessionLanguage::SimplifiedChinese;
	case ConfiguredLanguage::OriginalForSimplifiedChinese:
		return SessionLanguage::OriginalForSimplifiedChinese;
	case ConfiguredLanguage::Original:
	default:
		return SessionLanguage::Original;
	}
}

constexpr CompatibilityMessage ResolveMessage(
	ConfiguredLanguage selected,
	const LanguageEnvironment &environment)
{
	if (selected == ConfiguredLanguage::Automatic) {
		return CompatibilityMessage::None;
	}

	bool compatible = false;
	switch (environment.ae_language) {
	case AeLanguage::Japanese:
		compatible = selected == ConfiguredLanguage::Original;
		break;
	case AeLanguage::SimplifiedChinese:
		compatible =
			selected == ConfiguredLanguage::SimplifiedChinese ||
			selected == ConfiguredLanguage::OriginalForSimplifiedChinese;
		break;
	case AeLanguage::English:
		compatible = selected == ConfiguredLanguage::English;
		if (!compatible && environment.host_version == HostVersion::AtMost22) {
			if (environment.windows_code_page == WindowsCodePage::Japanese932) {
				compatible = selected == ConfiguredLanguage::Original;
			} else if (environment.windows_code_page == WindowsCodePage::SimplifiedChinese936) {
				compatible =
					selected == ConfiguredLanguage::SimplifiedChinese ||
					selected == ConfiguredLanguage::OriginalForSimplifiedChinese;
			}
		}
		break;
	case AeLanguage::Other:
	case AeLanguage::Unavailable:
	default:
		compatible = selected == ConfiguredLanguage::English;
		break;
	}

	return compatible
		? CompatibilityMessage::None
		: CompatibilityMessage::Incompatible;
}

} // namespace FsLanguage
