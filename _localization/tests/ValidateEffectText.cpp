#include "AeText.h"
#include "core/AeTextCatalog.h"

#include <cstdio>
#include <cstring>
#include <string>

#include <Windows.h>
#include <SPBasic.h>

namespace {

inline constexpr char kSuiteName[] = "Fixture Text Suite";
inline constexpr std::int32_t kSuiteVersion = 1;

enum class ResolveBehavior {
	Success,
	Failure,
	EmptyResult,
	MalformedStatic,
	PartialAbout,
	PartialError,
};

enum class AcquireBehavior {
	Failure,
	Missing,
	Available,
};

struct FakeState {
	AcquireBehavior acquire = AcquireBehavior::Failure;
	bool empty_suite = false;
	ResolveBehavior resolve = ResolveBehavior::Success;
	int acquire_calls = 0;
	int release_calls = 0;
	int resolve_calls = 0;
	int options_calls = 0;
	int requested_version = 0;
	std::string requested_name;
	std::wstring options_title;
};

FakeState *g_state = nullptr;
int g_failures = 0;

void Check(bool condition, const char *message)
{
	if (!condition) {
		std::fprintf(stderr, "FAILED: %s\n", message);
		++g_failures;
	}
}

bool Equal(const char *actual, const char *expected)
{
	return actual && std::strcmp(actual, expected) == 0;
}

SPAPI std::int32_t ResolveText(
	const AeText::CatalogView *,
	const AeText::TextRequest *request,
	AeText::TextResult *result)
{
	++g_state->resolve_calls;
	if (g_state->resolve == ResolveBehavior::Failure || !request || !result) {
		return -1;
	}
	if (g_state->resolve == ResolveBehavior::EmptyResult) {
		return AeText::kTextResolved;
	}
	if (g_state->resolve == ResolveBehavior::MalformedStatic &&
		request->token.role != AeText::TextRole::About &&
		request->token.role != AeText::TextRole::Error) {
		result->legacy = "malformed-static";
		result->utf8 = "unexpected-static-utf8";
		return AeText::kTextResolved;
	}
	if (g_state->resolve == ResolveBehavior::PartialAbout) {
		result->legacy = "partial-about";
		return AeText::kTextResolved;
	}
	if (g_state->resolve == ResolveBehavior::PartialError) {
		result->utf8 = "partial-error-utf8";
		return AeText::kTextResolved;
	}

	if (request->token.role == AeText::TextRole::About) {
		result->legacy = "translated-about";
		result->utf8 = "translated-about-utf8";
		return AeText::kTextResolved;
	}
	if (request->token.role == AeText::TextRole::Error) {
		result->legacy = "unused-translated-error-legacy";
		result->utf8 =
			"\xE9\x94\x99\xE8\xAF\xAF\x3A\x20\xE5\x8F\x82\xE6\x95\xB0"
			"\xE9\x94\x99\xE8\xAF\xAF\xE3\x80\x82";
		return AeText::kTextResolved;
	}

	result->legacy = "translated-static";
	return AeText::kTextResolved;
}

SPAPI void ShowOptions(std::uint64_t, const wchar_t *plugin_title)
{
	++g_state->options_calls;
	g_state->options_title = plugin_title ? plugin_title : L"";
}

const AeText::TextSuite1 kSuite{ResolveText, ShowOptions};
const AeText::TextSuite1 kEmptySuite{nullptr, nullptr};

SPAPI SPErr AcquireSuite(const char *name, std::int32_t version, const void **suite)
{
	++g_state->acquire_calls;
	g_state->requested_name = name ? name : "";
	g_state->requested_version = version;
	*suite = nullptr;
	if (g_state->acquire == AcquireBehavior::Failure) {
		return -1;
	}
	if (g_state->acquire == AcquireBehavior::Missing) {
		return 0;
	}
	*suite = g_state->empty_suite
		? static_cast<const void *>(&kEmptySuite)
		: static_cast<const void *>(&kSuite);
	return 0;
}

SPAPI SPErr ReleaseSuite(const char *name, std::int32_t version)
{
	Check(name && std::strcmp(name, kSuiteName) == 0,
		"Release used the wrong suite name.");
	Check(version == kSuiteVersion, "Release used the wrong suite version.");
	++g_state->release_calls;
	return 0;
}

SPBasicSuite MakeBasicSuite()
{
	SPBasicSuite basic{};
	basic.AcquireSuite = AcquireSuite;
	basic.ReleaseSuite = ReleaseSuite;
	return basic;
}

const char *const kParamOriginal[]{"original-param"};
const char *const kLabelOriginal[]{"original-label"};
const char *const kPopupOriginal[]{"original-popup"};
const char *const kTopicOriginal[]{"original-topic"};
const char *const kErrorOriginal[]{"original-error"};
const char *const kAboutOriginal[]{"original-about"};
const char *const kAboutUtf8Original[]{"original-about-utf8"};
const char *const kErrorUtf8Original[]{"original-error-utf8"};

const AeText::StringTable kOriginalRoles[]{
	{kParamOriginal, 1},
	{kLabelOriginal, 1},
	{kPopupOriginal, 1},
	{kTopicOriginal, 1},
	{kAboutOriginal, 1},
	{kErrorOriginal, 1},
};
const AeText::VariantView kOriginalVariant{
	sizeof(AeText::VariantView),
	6,
	"source",
	kOriginalRoles,
	AeText::kTextRoleCount,
	{kAboutUtf8Original, 1},
	{kErrorUtf8Original, 1},
};
const AeText::CatalogView kCatalog{
	sizeof(AeText::CatalogView),
	AeText::kCatalogVersion,
	&kOriginalVariant,
	1,
	0,
};

void CheckOriginalFallback(AeText::Client &text)
{
	Check(
		Equal(text.Static({AeText::TextRole::Param, 0}), "original-param"),
		"Param text did not fall back to the source variant.");
	Check(
		Equal(text.Static({AeText::TextRole::Label, 0}), "original-label"),
		"Label text did not fall back to the source variant.");
	Check(
		Equal(text.Static({AeText::TextRole::Popup, 0}), "original-popup"),
		"Popup text did not fall back to the source variant.");
	Check(
		Equal(text.Static({AeText::TextRole::Topic, 0}), "original-topic"),
		"Topic text did not fall back to the source variant.");
	Check(
		Equal(text.Error({AeText::TextRole::Error, 0}), "original-error-utf8"),
		"Error text did not convert the source UTF-8 fallback to Windows ACP.");

	const AeText::AboutText about = text.About({AeText::TextRole::About, 0});
	Check(
		Equal(AeText::detail::AboutTextAccess::Legacy(about), "original-about"),
		"About legacy text did not fall back to the source variant.");
	Check(
		Equal(AeText::detail::AboutTextAccess::ScriptUtf8(about), "original-about-utf8"),
		"About UTF-8 text did not fall back to the source variant.");
}

void CheckAcquireContract(const FakeState &state)
{
	Check(state.acquire_calls == 1, "Client did not acquire exactly once.");
	Check(state.requested_name == kSuiteName, "Client requested the wrong suite name.");
	Check(state.requested_version == 1,
		"Client requested a suite version other than the fixed V1 contract.");
}

void TestMissingSuite()
{
	FakeState state;
	state.acquire = AcquireBehavior::Missing;
	g_state = &state;
	SPBasicSuite basic = MakeBasicSuite();
	PF_InData in_data{};
	in_data.pica_basicP = &basic;

	{
		AeText::Client text(&in_data, kCatalog, kSuiteName, kSuiteVersion);
		CheckOriginalFallback(text);
		text.OpenSettings(L"Missing");
	}

	CheckAcquireContract(state);
	Check(state.release_calls == 0, "A missing suite was incorrectly released.");
	Check(state.options_calls == 0, "Options was not a no-op without the suite.");
}

void TestAcquireFailure()
{
	FakeState state;
	g_state = &state;
	SPBasicSuite basic = MakeBasicSuite();
	PF_InData in_data{};
	in_data.pica_basicP = &basic;

	{
		AeText::Client text(&in_data, kCatalog, kSuiteName, kSuiteVersion);
		CheckOriginalFallback(text);
		text.OpenSettings(L"Acquire failure");
	}

	CheckAcquireContract(state);
	Check(state.release_calls == 0, "A failed Acquire was incorrectly released.");
	Check(state.options_calls == 0, "Options was not a no-op after Acquire failed.");
}

void TestFailedResolve()
{
	FakeState state;
	state.acquire = AcquireBehavior::Available;
	state.resolve = ResolveBehavior::Failure;
	g_state = &state;
	SPBasicSuite basic = MakeBasicSuite();
	PF_InData in_data{};
	in_data.pica_basicP = &basic;

	{
		AeText::Client text(&in_data, kCatalog, kSuiteName, kSuiteVersion);
		CheckOriginalFallback(text);
	}

	CheckAcquireContract(state);
	Check(state.resolve_calls == 6, "The failure test did not exercise all text roles.");
	Check(state.release_calls == 1, "A successful Acquire was not released exactly once.");
}

void TestIncompleteSuiteResults()
{
	FakeState state;
	state.acquire = AcquireBehavior::Available;
	state.resolve = ResolveBehavior::EmptyResult;
	g_state = &state;
	SPBasicSuite basic = MakeBasicSuite();
	PF_InData in_data{};
	in_data.pica_basicP = &basic;

	{
		AeText::Client text(&in_data, kCatalog, kSuiteName, kSuiteVersion);
		CheckOriginalFallback(text);
	}
	Check(state.release_calls == 1, "An empty suite result broke Acquire/Release pairing.");

	state = {};
	state.acquire = AcquireBehavior::Available;
	state.resolve = ResolveBehavior::PartialAbout;
	g_state = &state;
	{
		AeText::Client text(&in_data, kCatalog, kSuiteName, kSuiteVersion);
		const AeText::AboutText about = text.About({AeText::TextRole::About, 0});
		Check(
			Equal(AeText::detail::AboutTextAccess::Legacy(about), "original-about"),
			"A partial About result mixed translated and source text.");
		Check(
			Equal(AeText::detail::AboutTextAccess::ScriptUtf8(about), "original-about-utf8"),
			"A partial About result mixed UTF-8 sources.");
	}
	Check(state.release_calls == 1, "A partial About result broke Acquire/Release pairing.");

	state = {};
	state.acquire = AcquireBehavior::Available;
	state.resolve = ResolveBehavior::PartialError;
	g_state = &state;
	{
		AeText::Client text(&in_data, kCatalog, kSuiteName, kSuiteVersion);
		Check(
			Equal(text.Error({AeText::TextRole::Error, 0}), "original-error-utf8"),
			"A partial Error result mixed translated and source text.");
	}
	Check(state.release_calls == 1, "A partial Error result broke Acquire/Release pairing.");
}

void TestMalformedStaticResult()
{
	FakeState state;
	state.acquire = AcquireBehavior::Available;
	state.resolve = ResolveBehavior::MalformedStatic;
	g_state = &state;
	SPBasicSuite basic = MakeBasicSuite();
	PF_InData in_data{};
	in_data.pica_basicP = &basic;

	{
		AeText::Client text(&in_data, kCatalog, kSuiteName, kSuiteVersion);
		Check(
			Equal(text.Static({AeText::TextRole::Param, 0}), "original-param"),
			"A malformed static result did not fall back wholly to source.");
	}
	Check(state.resolve_calls == 1, "The malformed static result was not exercised once.");
	Check(state.release_calls == 1, "A malformed static result broke Acquire/Release pairing.");
}

void TestEmptySuite()
{
	FakeState state;
	state.acquire = AcquireBehavior::Available;
	state.empty_suite = true;
	g_state = &state;
	SPBasicSuite basic = MakeBasicSuite();
	PF_InData in_data{};
	in_data.pica_basicP = &basic;

	{
		AeText::Client text(&in_data, kCatalog, kSuiteName, kSuiteVersion);
		CheckOriginalFallback(text);
		text.OpenSettings(L"Empty");
	}
	Check(state.resolve_calls == 0, "An empty suite called a missing Resolve function.");
	Check(state.options_calls == 0, "An empty suite called a missing Options function.");
	Check(state.release_calls == 1, "An acquired empty suite was not released.");
}

void TestResolvedText()
{
	FakeState state;
	state.acquire = AcquireBehavior::Available;
	g_state = &state;
	SPBasicSuite basic = MakeBasicSuite();
	PF_InData in_data{};
	in_data.pica_basicP = &basic;

	{
		AeText::Client text(&in_data, kCatalog, kSuiteName, kSuiteVersion);
		Check(
			Equal(text.Static({AeText::TextRole::Param, 0}), "translated-static"),
			"Static text did not use the available suite.");
		const char *error = text.Error({AeText::TextRole::Error, 0});
		Check(error && error[0] != '\0',
			"Error text did not convert the translated UTF-8 text to Windows ACP.");
		if (GetACP() == 936) {
			Check(
				Equal(error, "\xB4\xED\xCE\xF3\x3A\x20\xB2\xCE\xCA\xFD\xB4\xED\xCE\xF3\xA1\xA3"),
				"Error text did not produce the expected CP936 bytes on a CP936 system.");
		}

		const AeText::AboutText about = text.About({AeText::TextRole::About, 0});
		Check(
			Equal(AeText::detail::AboutTextAccess::Legacy(about), "translated-about"),
			"About legacy text did not use the suite.");
		Check(
			Equal(AeText::detail::AboutTextAccess::ScriptUtf8(about), "translated-about-utf8"),
			"About UTF-8 text did not use the suite.");
		text.OpenSettings(L"Resolved");
	}

	CheckAcquireContract(state);
	Check(state.resolve_calls == 3, "The success test did not exercise static/About/Error paths.");
	Check(state.options_calls == 1, "Options was not forwarded exactly once.");
	Check(state.options_title == L"Resolved", "Options changed the plugin title.");
	Check(state.release_calls == 1, "The available suite was not released exactly once.");
}

void TestInvalidCatalogsDoNotAcquire()
{
	FakeState state;
	state.acquire = AcquireBehavior::Available;
	g_state = &state;
	SPBasicSuite basic = MakeBasicSuite();
	PF_InData in_data{};
	in_data.pica_basicP = &basic;

	AeText::CatalogView invalid = kCatalog;
	invalid.fallback_variant_index = 1;
	Check(!AeText::detail::ValidCatalog(invalid), "An invalid fallback index was accepted.");
	{
		AeText::Client text(&in_data, invalid, kSuiteName, kSuiteVersion);
		Check(Equal(text.Static({AeText::TextRole::Param, 0}), ""),
			"An invalid catalog exposed fallback text.");
	}
	Check(state.acquire_calls == 0, "An invalid catalog acquired the runtime suite.");

	AeText::VariantView invalid_variant = kOriginalVariant;
	invalid_variant.role_table_count = AeText::kTextRoleCount - 1;
	invalid = kCatalog;
	invalid.variants = &invalid_variant;
	Check(!AeText::detail::ValidCatalog(invalid), "An invalid role-table count was accepted.");

	AeText::StringTable mismatched_roles[AeText::kTextRoleCount]{};
	for (std::uint32_t role = 0; role < AeText::kTextRoleCount; ++role) {
		mismatched_roles[role] = kOriginalRoles[role];
	}
	mismatched_roles[0] = {nullptr, 0};
	AeText::VariantView mismatched_variant = kOriginalVariant;
	mismatched_variant.stable_id_size = 2;
	mismatched_variant.stable_id = "en";
	mismatched_variant.role_tables = mismatched_roles;
	const AeText::VariantView mismatched_variants[]{
		kOriginalVariant,
		mismatched_variant,
	};
	invalid = kCatalog;
	invalid.variants = mismatched_variants;
	invalid.variant_count = 2;
	Check(!AeText::detail::ValidCatalog(invalid),
		"Mismatched Variant table counts were accepted.");
}

} // namespace

int main()
{
	static_assert(kSuiteVersion == 1);
	TestMissingSuite();
	TestAcquireFailure();
	TestFailedResolve();
	TestIncompleteSuiteResults();
	TestMalformedStaticResult();
	TestEmptySuite();
	TestResolvedText();
	TestInvalidCatalogsDoNotAcquire();
	if (g_failures != 0) {
		std::fprintf(stderr, "%d AeText client contract test(s) failed.\n", g_failures);
		return 1;
	}
	std::puts("AeText client contract validation passed.");
	return 0;
}
