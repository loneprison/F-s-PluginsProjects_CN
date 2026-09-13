#pragma once

#include "LanguagePolicy.h"

#include <cstdint>
#include <filesystem>

namespace FsLanguage {

enum class SettingsUiLanguage : std::uint8_t {
	English,
	SimplifiedChinese,
	Japanese
};

enum class RecoveryStatus : std::uint8_t {
	None,
	DefaultsRepaired,
	FieldsRepaired,
	BackupFailed,
	RepairWriteFailed
};

struct LoadedSettings {
	ConfiguredLanguage language = ConfiguredLanguage::Automatic;
	SettingsUiLanguage ui_language = SettingsUiLanguage::English;
	bool file_exists = false;
	bool valid = true;
	bool version_mismatch = false;
	bool used_field_defaults = false;
	RecoveryStatus recovery = RecoveryStatus::None;
};

enum class SaveError : std::uint8_t {
	None,
	ConfigDirectoryUnavailable,
	ConfigBusy,
	DirectoryCreationFailed,
	TemporaryFileCreationFailed,
	SafeReplaceFailed
};

std::filesystem::path LanguageConfigPath();

LoadedSettings LoadAndRepair(
	const std::filesystem::path &path,
	SettingsUiLanguage default_ui_language);

SaveError SaveLanguageSettings(
	const std::filesystem::path &path,
	ConfiguredLanguage language,
	SettingsUiLanguage ui_language);

} // namespace FsLanguage
