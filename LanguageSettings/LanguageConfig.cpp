#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0600
#endif

#include "LanguageConfig.h"

#include "SettingsText.generated.h"

#include "../FsLibrary/json.hpp"

#include <Windows.h>
#include <ShlObj.h>

#include <fstream>
#include <sstream>
#include <string>

#pragma comment(lib, "Shell32.lib")

namespace FsLanguage {
namespace {

class UniqueHandle final {
public:
	explicit UniqueHandle(HANDLE handle = nullptr) noexcept
		: handle_(handle)
	{}

	~UniqueHandle() noexcept
	{
		Close();
	}

	UniqueHandle(const UniqueHandle &) = delete;
	UniqueHandle &operator=(const UniqueHandle &) = delete;

	HANDLE Get() const noexcept { return handle_; }
	bool Valid() const noexcept
	{
		return handle_ && handle_ != INVALID_HANDLE_VALUE;
	}

	void Close() noexcept
	{
		if (Valid()) {
			CloseHandle(handle_);
		}
		handle_ = nullptr;
	}

private:
	HANDLE handle_;
};

class ConfigLock final {
public:
	ConfigLock() noexcept
		: handle_(CreateMutexW(
			nullptr,
			FALSE,
			FsLanguageSettingsText::kConfigMutexName))
	{
		if (handle_.Valid()) {
			const DWORD result = WaitForSingleObject(handle_.Get(), 5000);
			locked_ = result == WAIT_OBJECT_0 || result == WAIT_ABANDONED;
		}
	}

	~ConfigLock() noexcept
	{
		if (locked_) {
			ReleaseMutex(handle_.Get());
		}
	}

	ConfigLock(const ConfigLock &) = delete;
	ConfigLock &operator=(const ConfigLock &) = delete;

	bool IsLocked() const noexcept { return locked_; }

private:
	UniqueHandle handle_;
	bool locked_ = false;
};

const char *LanguageKey(ConfiguredLanguage language)
{
	switch (language) {
	case ConfiguredLanguage::English: return "en";
	case ConfiguredLanguage::Original: return "ja";
	case ConfiguredLanguage::SimplifiedChinese: return "zh";
	case ConfiguredLanguage::OriginalForSimplifiedChinese: return "ja_for_zh";
	case ConfiguredLanguage::Automatic:
	default: return "auto";
	}
}

const char *UiLanguageKey(SettingsUiLanguage language)
{
	switch (language) {
	case SettingsUiLanguage::SimplifiedChinese: return "zh";
	case SettingsUiLanguage::Japanese: return "ja";
	case SettingsUiLanguage::English:
	default: return "en";
	}
}

bool TryParseLanguage(const std::string &value, ConfiguredLanguage &language)
{
	if (value == "auto") {
		language = ConfiguredLanguage::Automatic;
		return true;
	}
	if (value == "en") {
		language = ConfiguredLanguage::English;
		return true;
	}
	if (value == "ja") {
		language = ConfiguredLanguage::Original;
		return true;
	}
	if (value == "zh") {
		language = ConfiguredLanguage::SimplifiedChinese;
		return true;
	}
	if (value == "ja_for_zh") {
		language = ConfiguredLanguage::OriginalForSimplifiedChinese;
		return true;
	}
	return false;
}

bool TryParseUiLanguage(const std::string &value, SettingsUiLanguage &language)
{
	if (value == "en") {
		language = SettingsUiLanguage::English;
		return true;
	}
	if (value == "zh") {
		language = SettingsUiLanguage::SimplifiedChinese;
		return true;
	}
	if (value == "ja") {
		language = SettingsUiLanguage::Japanese;
		return true;
	}
	return false;
}

SaveError SaveLocked(
	const std::filesystem::path &path,
	ConfiguredLanguage language,
	SettingsUiLanguage ui_language)
{
	std::error_code directory_error;
	std::filesystem::create_directories(path.parent_path(), directory_error);
	if (directory_error) {
		return SaveError::DirectoryCreationFailed;
	}

	nlohmann::json root = {
		{ "version", 1 },
		{ "language", LanguageKey(language) },
		{ "settings_ui_language", UiLanguageKey(ui_language) }
	};
	const std::string contents = root.dump(2) + "\n";

	std::wostringstream temp_name;
	temp_name << path.wstring()
			  << L'.'
			  << GetCurrentProcessId()
			  << L'.'
			  << GetCurrentThreadId()
			  << L".tmp";
	const std::filesystem::path temp_path(temp_name.str());

	UniqueHandle file(CreateFileW(
		temp_path.c_str(),
		GENERIC_WRITE,
		0,
		nullptr,
		CREATE_ALWAYS,
		FILE_ATTRIBUTE_TEMPORARY,
		nullptr));
	if (!file.Valid()) {
		return SaveError::TemporaryFileCreationFailed;
	}

	DWORD bytes_written = 0;
	const bool write_succeeded =
		WriteFile(
			file.Get(),
			contents.data(),
			static_cast<DWORD>(contents.size()),
			&bytes_written,
			nullptr) != FALSE &&
		bytes_written == contents.size() &&
		FlushFileBuffers(file.Get()) != FALSE;
	file.Close();

	if (!write_succeeded ||
		!MoveFileExW(
			temp_path.c_str(),
			path.c_str(),
			MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) {
		DeleteFileW(temp_path.c_str());
		return SaveError::SafeReplaceFailed;
	}

	return SaveError::None;
}

bool BackupInvalidFile(const std::filesystem::path &path)
{
	std::error_code error;
	std::filesystem::copy_file(
		path,
		path.parent_path() / FsLanguageSettingsText::kInvalidConfigBackupFileName,
		std::filesystem::copy_options::overwrite_existing,
		error);
	return !error;
}

void RepairInvalidFile(
	LoadedSettings &settings,
	const std::filesystem::path &path,
	RecoveryStatus success_status)
{
	settings.valid = false;
	if (!BackupInvalidFile(path)) {
		settings.recovery = RecoveryStatus::BackupFailed;
		return;
	}

	if (SaveLocked(path, settings.language, settings.ui_language) != SaveError::None) {
		settings.recovery = RecoveryStatus::RepairWriteFailed;
		return;
	}

	settings.valid = true;
	settings.recovery = success_status;
}

} // namespace

std::filesystem::path LanguageConfigPath()
{
	wchar_t local_app_data[MAX_PATH] = {};
	if (FAILED(SHGetFolderPathW(
			nullptr,
			CSIDL_LOCAL_APPDATA | CSIDL_FLAG_CREATE,
			nullptr,
			SHGFP_TYPE_CURRENT,
			local_app_data))) {
		return {};
	}

	return std::filesystem::path(local_app_data) /
		FsLanguageSettingsText::kConfigDirectoryName /
		FsLanguageSettingsText::kConfigFileName;
}

LoadedSettings LoadAndRepair(
	const std::filesystem::path &path,
	SettingsUiLanguage default_ui_language)
{
	LoadedSettings settings;
	settings.ui_language = default_ui_language;

	std::error_code error;
	settings.file_exists = std::filesystem::exists(path, error);
	if (error || !settings.file_exists) {
		settings.valid = !error;
		return settings;
	}

	ConfigLock lock;
	if (!lock.IsLocked()) {
		settings.valid = false;
		return settings;
	}

	std::ifstream input(path, std::ios::binary);
	if (!input) {
		settings.valid = false;
		return settings;
	}

	const nlohmann::json root = nlohmann::json::parse(input, nullptr, false);
	input.close();
	if (!root.is_object()) {
		settings.language = ConfiguredLanguage::Automatic;
		settings.ui_language = default_ui_language;
		RepairInvalidFile(settings, path, RecoveryStatus::DefaultsRepaired);
		return settings;
	}

	const auto version = root.find("version");
	const auto language = root.find("language");
	const auto ui_language = root.find("settings_ui_language");
	const bool current_version =
		version != root.end() &&
		version->is_number_integer() &&
		*version == 1;
	const bool language_valid =
		language != root.end() &&
		language->is_string() &&
		TryParseLanguage(language->get<std::string>(), settings.language);
	const bool ui_language_valid =
		ui_language != root.end() &&
		ui_language->is_string() &&
		TryParseUiLanguage(ui_language->get<std::string>(), settings.ui_language);

	if (!language_valid) {
		settings.language = ConfiguredLanguage::Automatic;
	}
	if (!ui_language_valid) {
		settings.ui_language = default_ui_language;
	}
	settings.used_field_defaults = !language_valid || !ui_language_valid;

	if (!current_version) {
		settings.version_mismatch = true;
		return settings;
	}

	if (settings.used_field_defaults) {
		RepairInvalidFile(settings, path, RecoveryStatus::FieldsRepaired);
	}
	return settings;
}

SaveError SaveLanguageSettings(
	const std::filesystem::path &path,
	ConfiguredLanguage language,
	SettingsUiLanguage ui_language)
{
	if (path.empty()) {
		return SaveError::ConfigDirectoryUnavailable;
	}

	ConfigLock lock;
	if (!lock.IsLocked()) {
		return SaveError::ConfigBusy;
	}
	return SaveLocked(path, language, ui_language);
}

} // namespace FsLanguage
