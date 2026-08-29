#include "../AeText.h"

#include "AeTextCatalog.h"

#include <cstdint>

#include <AE_EffectCB.h>
#include <SPBasic.h>
#include <Windows.h>

namespace AeText {
namespace {

inline constexpr char kEmptyText[] = "";

bool IsStatic(TextRole role) noexcept
{
	return role == TextRole::Param ||
		role == TextRole::Label ||
		role == TextRole::Popup ||
		role == TextRole::Topic;
}

bool Utf8ToWindowsAcp(
	const char *utf8,
	char *output,
	int output_capacity) noexcept
{
	if (!utf8 || !output || output_capacity <= 0) {
		return false;
	}

	wchar_t wide[PF_MAX_EFFECT_MSG_LEN + 1]{};
	const int wide_length = MultiByteToWideChar(
		CP_UTF8,
		MB_ERR_INVALID_CHARS,
		utf8,
		-1,
		wide,
		static_cast<int>(sizeof(wide) / sizeof(wide[0])));
	if (wide_length == 0) {
		return false;
	}

	const UINT code_page = GetACP();
	const bool utf8_acp = code_page == CP_UTF8;
	BOOL used_default = FALSE;
	return WideCharToMultiByte(
		code_page,
		utf8_acp ? WC_ERR_INVALID_CHARS : WC_NO_BEST_FIT_CHARS,
		wide,
		wide_length,
		output,
		output_capacity,
		utf8_acp ? nullptr : "?",
		utf8_acp ? nullptr : &used_default) != 0;
}

std::uint64_t MainWindow(PF_InData *in_data) noexcept
{
	void *window = nullptr;
	if (in_data && in_data->utils && in_data->utils->get_platform_data &&
		in_data->utils->get_platform_data(
			in_data->effect_ref,
			PF_PlatData_MAIN_WND,
			&window) != PF_Err_NONE) {
		window = nullptr;
	}
	return static_cast<std::uint64_t>(reinterpret_cast<std::uintptr_t>(window));
}

const VariantView *Fallback(const CatalogView *catalog) noexcept
{
	return catalog ? detail::FallbackVariant(*catalog) : nullptr;
}

} // namespace

Client::Client(
	PF_InData *in_data,
	const CatalogView &catalog,
	const char *suite_name,
	std::int32_t suite_version) noexcept
	: in_data_(in_data),
	  pica_basic_(in_data ? in_data->pica_basicP : nullptr),
	  catalog_(&catalog),
	  suite_name_(suite_name),
	  suite_version_(suite_version),
	  suite_(nullptr),
	  error_legacy_{}
{
	if (!detail::ValidCatalog(catalog) ||
		!suite_name_ || !suite_name_[0] ||
		!pica_basic_ || !pica_basic_->AcquireSuite) {
		return;
	}

	const void *suite = nullptr;
	if (pica_basic_->AcquireSuite(suite_name_, suite_version_, &suite) == 0 && suite) {
		suite_ = static_cast<const TextSuite1 *>(suite);
	}
}

Client::~Client() noexcept
{
	if (suite_ && pica_basic_ && pica_basic_->ReleaseSuite) {
		pica_basic_->ReleaseSuite(suite_name_, suite_version_);
	}
}

bool Client::Resolve(const TextRequest &request, TextResult &result) const noexcept
{
	result = {};
	if (!suite_ || !suite_->Resolve ||
		suite_->Resolve(catalog_, &request, &result) != kTextResolved) {
		result = {};
		return false;
	}
	if (IsStatic(request.token.role)) {
		if (!result.legacy || result.utf8) {
			result = {};
			return false;
		}
		return true;
	}
	if (request.token.role == TextRole::About ||
		request.token.role == TextRole::Error) {
		if (!result.legacy || !result.utf8) {
			result = {};
			return false;
		}
		return true;
	}
	result = {};
	return false;
}

const char *Client::Static(TextToken token) const noexcept
{
	if (!IsStatic(token.role)) {
		return kEmptyText;
	}
	const TextRequest request{token};
	TextResult result{};
	if (Resolve(request, result)) {
		return result.legacy;
	}
	const VariantView *fallback = Fallback(catalog_);
	const char *value = fallback ? detail::LegacyValue(*fallback, token) : nullptr;
	return value ? value : kEmptyText;
}

const char *Client::Error(TextToken token) const noexcept
{
	if (token.role != TextRole::Error) {
		return kEmptyText;
	}
	const VariantView *fallback = Fallback(catalog_);
	const char *utf8 = fallback ? detail::Utf8Value(*fallback, token) : nullptr;
	const TextRequest request{token};
	TextResult result{};
	if (Resolve(request, result)) {
		utf8 = result.utf8;
	}
	if (Utf8ToWindowsAcp(
		utf8,
		error_legacy_,
		static_cast<int>(sizeof(error_legacy_)))) {
		return error_legacy_;
	}
	const char *legacy = fallback ? detail::LegacyValue(*fallback, token) : nullptr;
	return legacy ? legacy : kEmptyText;
}

AboutText Client::About(TextToken token) const noexcept
{
	if (token.role != TextRole::About) {
		return AboutText(kEmptyText, kEmptyText);
	}
	const VariantView *fallback = Fallback(catalog_);
	const char *legacy = fallback ? detail::LegacyValue(*fallback, token) : nullptr;
	const char *utf8 = fallback ? detail::Utf8Value(*fallback, token) : nullptr;
	const TextRequest request{token};
	TextResult result{};
	if (Resolve(request, result)) {
		return AboutText(result.utf8, result.legacy);
	}
	return AboutText(utf8 ? utf8 : kEmptyText, legacy ? legacy : kEmptyText);
}

LegacyAboutText Client::LegacyAbout(TextToken token) const noexcept
{
	const AboutText text = About(token);
	return {
		detail::AboutTextAccess::ScriptUtf8(text),
		detail::AboutTextAccess::Legacy(text)};
}

void Client::OpenSettings(const wchar_t *plugin_title) const noexcept
{
	if (suite_ && suite_->ShowOptions) {
		suite_->ShowOptions(MainWindow(in_data_), plugin_title ? plugin_title : L"");
	}
}

} // namespace AeText
