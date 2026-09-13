#include "../AeText.h"

#include "AeTextCatalog.h"

#include <cstdint>

#include <AE_EffectCB.h>
#include <SPBasic.h>
#include <Windows.h>

namespace AeText {
namespace {

bool Utf8ToWindowsAcp(
	const char *utf8,
	char *output,
	int output_capacity) noexcept
{
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

#if !defined(AETEXTCLIENT_RUNTIME_DISABLED)
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
#endif

} // namespace

Client::Client(
	PF_InData *in_data,
	const CatalogView &catalog,
	const char *suite_name,
	std::int32_t suite_version) noexcept
	: in_data_(in_data),
#if defined(AETEXTCLIENT_RUNTIME_DISABLED)
	  pica_basic_(nullptr),
	  catalog_(&catalog),
	  suite_name_(nullptr),
	  suite_version_(0),
#else
	  pica_basic_(in_data ? in_data->pica_basicP : nullptr),
	  catalog_(&catalog),
	  suite_name_(suite_name),
	  suite_version_(suite_version),
#endif
	  suite_(nullptr),
	  error_legacy_{}
{
#if !defined(AETEXTCLIENT_RUNTIME_DISABLED)
	if (!pica_basic_ || !pica_basic_->AcquireSuite) {
		return;
	}

	const void *suite = nullptr;
	if (pica_basic_->AcquireSuite(suite_name_, suite_version_, &suite) == 0 && suite) {
		suite_ = static_cast<const TextSuite1 *>(suite);
	}
#else
	(void)suite_name;
	(void)suite_version;
#endif
}

Client::~Client() noexcept
{
#if !defined(AETEXTCLIENT_RUNTIME_DISABLED)
	if (suite_ && pica_basic_ && pica_basic_->ReleaseSuite) {
		pica_basic_->ReleaseSuite(suite_name_, suite_version_);
	}
#endif
}

bool Client::Resolve(const TextRequest &request, TextResult &result) const noexcept
{
#if defined(AETEXTCLIENT_RUNTIME_DISABLED)
	(void)request;
	(void)result;
	return false;
#else
	if (!suite_ || !suite_->Resolve ||
		suite_->Resolve(catalog_, &request, &result) != kTextResolved) {
		return false;
	}
	const bool requires_utf8 = request.token.role == TextRole::About ||
		request.token.role == TextRole::Error;
	return result.legacy && (requires_utf8 ? result.utf8 != nullptr : result.utf8 == nullptr);
#endif
}

const char *Client::Static(TextToken token) const noexcept
{
	const TextRequest request{token};
	TextResult result{};
	if (Resolve(request, result)) {
		return result.legacy;
	}
	return detail::LegacyValue(*detail::FallbackVariant(*catalog_), token);
}

const char *Client::Error(TextToken token) const noexcept
{
	const VariantView &fallback = *detail::FallbackVariant(*catalog_);
	const char *utf8 = detail::Utf8Value(fallback, token);
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
	return detail::LegacyValue(fallback, token);
}

AboutText Client::About(TextToken token) const noexcept
{
	const TextRequest request{token};
	TextResult result{};
	if (Resolve(request, result)) {
		return AboutText(result.utf8, result.legacy);
	}
	const VariantView &fallback = *detail::FallbackVariant(*catalog_);
	return AboutText(detail::Utf8Value(fallback, token), detail::LegacyValue(fallback, token));
}

void Client::OpenSettings(const wchar_t *plugin_title) const noexcept
{
#if defined(AETEXTCLIENT_RUNTIME_DISABLED)
	(void)plugin_title;
#else
	if (suite_ && suite_->ShowOptions) {
		suite_->ShowOptions(MainWindow(in_data_), plugin_title ? plugin_title : L"");
	}
#endif
}

} // namespace AeText
