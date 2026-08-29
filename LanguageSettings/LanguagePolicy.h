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
	AutomaticEnglishLegacyOtherWindows,
	AutomaticEnglishModern,
	AutomaticUnknownAe,
	AutomaticAeUnavailable,
	ManualEnglish,
	ManualJapaneseOtherLanguage,
	ManualSimplifiedChineseRecommended,
	ManualSimplifiedChineseOriginalRisk,
	ManualSimplifiedChineseOriginalForSimplifiedChinese,
	ManualEnglishModernOriginalOrSimplifiedChineseRisk,
	ManualEnglishModernOriginalForSimplifiedChineseRisk,
	ManualEnglishLegacyOriginalJapanese,
	ManualEnglishLegacyOriginalMismatch,
	ManualEnglishLegacySimplifiedChineseOnSimplifiedChineseWindows,
	ManualEnglishLegacySimplifiedChineseMismatch,
	ManualEnglishLegacyOriginalForSimplifiedChineseOnSimplifiedChineseWindows,
	ManualEnglishLegacyOriginalForSimplifiedChineseMismatch,
	ManualUnknownAe,
	ManualAeUnavailable
};

struct LanguageEnvironment {
	AeLanguage ae_language;
	HostVersion host_version;
	WindowsCodePage windows_code_page;
};

constexpr SessionLanguage ResolveAutomatic(const LanguageEnvironment &environment)
{
	switch (environment.ae_language) {
	case AeLanguage::SimplifiedChinese:
		return SessionLanguage::SimplifiedChinese;
	case AeLanguage::Japanese:
		return SessionLanguage::Original;
	case AeLanguage::English:
		if (environment.host_version == HostVersion::AtMost22 &&
			environment.windows_code_page == WindowsCodePage::SimplifiedChinese936) {
			return SessionLanguage::SimplifiedChinese;
		}
		return SessionLanguage::Original;
	case AeLanguage::Other:
	case AeLanguage::Unavailable:
	default:
		return SessionLanguage::Original;
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
	if (selected == ConfiguredLanguage::English) {
		return CompatibilityMessage::ManualEnglish;
	}

	if (selected == ConfiguredLanguage::Automatic) {
		switch (environment.ae_language) {
		case AeLanguage::SimplifiedChinese:
		case AeLanguage::Japanese:
			return CompatibilityMessage::None;
		case AeLanguage::English:
			if (environment.host_version == HostVersion::AtMost22) {
				return environment.windows_code_page == WindowsCodePage::OtherOrUnknown
					? CompatibilityMessage::AutomaticEnglishLegacyOtherWindows
					: CompatibilityMessage::None;
			}
			return CompatibilityMessage::AutomaticEnglishModern;
		case AeLanguage::Other:
			return CompatibilityMessage::AutomaticUnknownAe;
		case AeLanguage::Unavailable:
		default:
			return CompatibilityMessage::AutomaticAeUnavailable;
		}
	}

	switch (environment.ae_language) {
	case AeLanguage::Japanese:
		return selected == ConfiguredLanguage::Original
			? CompatibilityMessage::None
			: CompatibilityMessage::ManualJapaneseOtherLanguage;
	case AeLanguage::SimplifiedChinese:
		switch (selected) {
		case ConfiguredLanguage::SimplifiedChinese:
			return CompatibilityMessage::ManualSimplifiedChineseRecommended;
		case ConfiguredLanguage::OriginalForSimplifiedChinese:
			return CompatibilityMessage::ManualSimplifiedChineseOriginalForSimplifiedChinese;
		case ConfiguredLanguage::Original:
		default:
			return CompatibilityMessage::ManualSimplifiedChineseOriginalRisk;
		}
	case AeLanguage::English:
		if (environment.host_version == HostVersion::AtLeast23OrUnknown) {
			return selected == ConfiguredLanguage::OriginalForSimplifiedChinese
				? CompatibilityMessage::ManualEnglishModernOriginalForSimplifiedChineseRisk
				: CompatibilityMessage::ManualEnglishModernOriginalOrSimplifiedChineseRisk;
		}
		if (selected == ConfiguredLanguage::Original) {
			return environment.windows_code_page == WindowsCodePage::Japanese932
				? CompatibilityMessage::ManualEnglishLegacyOriginalJapanese
				: CompatibilityMessage::ManualEnglishLegacyOriginalMismatch;
		}
		if (selected == ConfiguredLanguage::SimplifiedChinese) {
			return environment.windows_code_page == WindowsCodePage::SimplifiedChinese936
				? CompatibilityMessage::ManualEnglishLegacySimplifiedChineseOnSimplifiedChineseWindows
				: CompatibilityMessage::ManualEnglishLegacySimplifiedChineseMismatch;
		}
		return environment.windows_code_page == WindowsCodePage::SimplifiedChinese936
			? CompatibilityMessage::ManualEnglishLegacyOriginalForSimplifiedChineseOnSimplifiedChineseWindows
			: CompatibilityMessage::ManualEnglishLegacyOriginalForSimplifiedChineseMismatch;
	case AeLanguage::Other:
		return CompatibilityMessage::ManualUnknownAe;
	case AeLanguage::Unavailable:
	default:
		return CompatibilityMessage::ManualAeUnavailable;
	}
}

namespace PolicyChecks {

inline constexpr LanguageEnvironment kSimplifiedChineseModern {
	AeLanguage::SimplifiedChinese,
	HostVersion::AtLeast23OrUnknown,
	WindowsCodePage::OtherOrUnknown
};
inline constexpr LanguageEnvironment kJapaneseModern {
	AeLanguage::Japanese,
	HostVersion::AtLeast23OrUnknown,
	WindowsCodePage::OtherOrUnknown
};
inline constexpr LanguageEnvironment kEnglishLegacySimplifiedChinese {
	AeLanguage::English,
	HostVersion::AtMost22,
	WindowsCodePage::SimplifiedChinese936
};
inline constexpr LanguageEnvironment kEnglishLegacyJapanese {
	AeLanguage::English,
	HostVersion::AtMost22,
	WindowsCodePage::Japanese932
};
inline constexpr LanguageEnvironment kEnglishLegacyOther {
	AeLanguage::English,
	HostVersion::AtMost22,
	WindowsCodePage::OtherOrUnknown
};
inline constexpr LanguageEnvironment kEnglishModern {
	AeLanguage::English,
	HostVersion::AtLeast23OrUnknown,
	WindowsCodePage::SimplifiedChinese936
};
inline constexpr LanguageEnvironment kUnknownModern {
	AeLanguage::Other,
	HostVersion::AtLeast23OrUnknown,
	WindowsCodePage::OtherOrUnknown
};
inline constexpr LanguageEnvironment kUnavailableModern {
	AeLanguage::Unavailable,
	HostVersion::AtLeast23OrUnknown,
	WindowsCodePage::OtherOrUnknown
};

static_assert(ResolveAutomatic(kSimplifiedChineseModern) == SessionLanguage::SimplifiedChinese);
static_assert(ResolveAutomatic(kJapaneseModern) == SessionLanguage::Original);
static_assert(ResolveAutomatic(kEnglishLegacySimplifiedChinese) == SessionLanguage::SimplifiedChinese);
static_assert(ResolveAutomatic(kEnglishLegacyJapanese) == SessionLanguage::Original);
static_assert(ResolveAutomatic(kEnglishModern) == SessionLanguage::Original);
static_assert(ResolveAutomatic(kUnknownModern) == SessionLanguage::Original);
static_assert(ResolveAutomatic(kUnavailableModern) == SessionLanguage::Original);
static_assert(ResolveMessage(ConfiguredLanguage::Automatic, kEnglishModern) == CompatibilityMessage::AutomaticEnglishModern);
static_assert(ResolveMessage(ConfiguredLanguage::Automatic, kEnglishLegacyOther) == CompatibilityMessage::AutomaticEnglishLegacyOtherWindows);
static_assert(ResolveMessage(ConfiguredLanguage::Automatic, kUnknownModern) == CompatibilityMessage::AutomaticUnknownAe);
static_assert(ResolveMessage(ConfiguredLanguage::Automatic, kUnavailableModern) == CompatibilityMessage::AutomaticAeUnavailable);
static_assert(ResolveMessage(ConfiguredLanguage::English, kSimplifiedChineseModern) == CompatibilityMessage::ManualEnglish);
static_assert(ResolveMessage(ConfiguredLanguage::Original, kJapaneseModern) == CompatibilityMessage::None);
static_assert(ResolveMessage(ConfiguredLanguage::SimplifiedChinese, kJapaneseModern) == CompatibilityMessage::ManualJapaneseOtherLanguage);
static_assert(ResolveMessage(ConfiguredLanguage::SimplifiedChinese, kSimplifiedChineseModern) == CompatibilityMessage::ManualSimplifiedChineseRecommended);
static_assert(ResolveMessage(ConfiguredLanguage::Original, kSimplifiedChineseModern) == CompatibilityMessage::ManualSimplifiedChineseOriginalRisk);
static_assert(ResolveMessage(ConfiguredLanguage::OriginalForSimplifiedChinese, kSimplifiedChineseModern) == CompatibilityMessage::ManualSimplifiedChineseOriginalForSimplifiedChinese);
static_assert(ResolveMessage(ConfiguredLanguage::Original, kEnglishModern) == CompatibilityMessage::ManualEnglishModernOriginalOrSimplifiedChineseRisk);
static_assert(ResolveMessage(ConfiguredLanguage::OriginalForSimplifiedChinese, kEnglishModern) == CompatibilityMessage::ManualEnglishModernOriginalForSimplifiedChineseRisk);
static_assert(ResolveMessage(ConfiguredLanguage::Original, kEnglishLegacyJapanese) == CompatibilityMessage::ManualEnglishLegacyOriginalJapanese);
static_assert(ResolveMessage(ConfiguredLanguage::Original, kEnglishLegacySimplifiedChinese) == CompatibilityMessage::ManualEnglishLegacyOriginalMismatch);
static_assert(ResolveMessage(ConfiguredLanguage::SimplifiedChinese, kEnglishLegacySimplifiedChinese) == CompatibilityMessage::ManualEnglishLegacySimplifiedChineseOnSimplifiedChineseWindows);
static_assert(ResolveMessage(ConfiguredLanguage::SimplifiedChinese, kEnglishLegacyJapanese) == CompatibilityMessage::ManualEnglishLegacySimplifiedChineseMismatch);
static_assert(ResolveMessage(ConfiguredLanguage::OriginalForSimplifiedChinese, kEnglishLegacySimplifiedChinese) == CompatibilityMessage::ManualEnglishLegacyOriginalForSimplifiedChineseOnSimplifiedChineseWindows);
static_assert(ResolveMessage(ConfiguredLanguage::OriginalForSimplifiedChinese, kEnglishLegacyJapanese) == CompatibilityMessage::ManualEnglishLegacyOriginalForSimplifiedChineseMismatch);
static_assert(ResolveMessage(ConfiguredLanguage::OriginalForSimplifiedChinese, kUnknownModern) == CompatibilityMessage::ManualUnknownAe);
static_assert(ResolveMessage(ConfiguredLanguage::OriginalForSimplifiedChinese, kUnavailableModern) == CompatibilityMessage::ManualAeUnavailable);

} // namespace PolicyChecks

} // namespace FsLanguage
