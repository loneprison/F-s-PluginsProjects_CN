#pragma once

#include <cstdint>

#include <AE_Effect.h>
#include <SPTypes.h>

#if !defined(_WIN32) || !defined(_WIN64) || !defined(_MSC_VER)
#error AeText V1 is a Windows x64 MSVC ABI.
#endif

namespace AeText {

inline constexpr std::uint32_t kCatalogVersion = 1;
inline constexpr std::uint32_t kTextRoleCount = 6;
inline constexpr std::int32_t kTextResolved = 0;

enum class TextRole : std::uint32_t {
	Param = 0,
	Label = 1,
	Popup = 2,
	Topic = 3,
	About = 4,
	Error = 5,
};

#pragma pack(push, 8)

// V1 is a Windows x64 MSVC ABI. Catalogs, variants, tables, and their strings
// are static read-only data owned by the effect AEX. Runtime Resolve() may read
// them only for the duration of that call and must not retain their pointers.
struct TextToken {
	TextRole role;
	std::uint32_t index;
};

struct StringTable {
	const char *const *values;
	std::uint32_t count;
};

struct VariantView {
	std::uint32_t struct_size;
	std::uint32_t stable_id_size; // ASCII bytes; excludes an optional trailing NUL.
	const char *stable_id;
	const StringTable *role_tables;
	std::uint32_t role_table_count;
	StringTable about_utf8;
	StringTable error_utf8;
};

struct CatalogView {
	std::uint32_t struct_size;
	std::uint32_t version;
	const VariantView *variants;
	std::uint32_t variant_count;
	std::uint32_t fallback_variant_index;
};

struct TextRequest {
	TextToken token;
};

struct TextResult {
	// Successful pointers refer to the effect AEX's static generated tables and
	// remain usable only while that AEX is loaded.
	const char *legacy;
	const char *utf8;
};

struct TextSuite1 {
	SPAPI std::int32_t (*Resolve)(
		const CatalogView *catalog,
		const TextRequest *request,
		TextResult *result);

	SPAPI void (*ShowOptions)(
		std::uint64_t owner_window,
		const wchar_t *plugin_title); // plugin_title is valid only for this call.
};

#pragma pack(pop)

namespace detail {
struct AboutTextAccess;
}

class AboutText final {
private:
	friend class Client;
	friend struct detail::AboutTextAccess;

	constexpr AboutText(const char *script_utf8, const char *legacy) noexcept
		: script_utf8_(script_utf8), legacy_(legacy)
	{}

	const char *script_utf8_;
	const char *legacy_;
};

namespace detail {
struct AboutTextAccess final {
	static constexpr const char *ScriptUtf8(const AboutText &text) noexcept
	{
		return text.script_utf8_;
	}

	static constexpr const char *Legacy(const AboutText &text) noexcept
	{
		return text.legacy_;
	}
};
}

// Short-lived effect-side client. The supplied suite identity is family-owned.
class Client final {
public:
	Client(
		PF_InData *in_data,
		const CatalogView &catalog,
		const char *suite_name,
		std::int32_t suite_version) noexcept;
	~Client() noexcept;

	Client(const Client &) = delete;
	Client &operator=(const Client &) = delete;
	Client(Client &&) = delete;
	Client &operator=(Client &&) = delete;

	const char *Static(TextToken token) const noexcept;
	const char *Error(TextToken token) const noexcept;
	AboutText About(TextToken token) const noexcept;
	void OpenSettings(const wchar_t *plugin_title) const noexcept;

private:
	bool Resolve(const TextRequest &request, TextResult &result) const noexcept;

	PF_InData *in_data_;
	SPBasicSuite *pica_basic_;
	const CatalogView *catalog_;
	const char *suite_name_;
	std::int32_t suite_version_;
	const TextSuite1 *suite_;
	mutable char error_legacy_[PF_MAX_EFFECT_MSG_LEN + 1];
};

} // namespace AeText
