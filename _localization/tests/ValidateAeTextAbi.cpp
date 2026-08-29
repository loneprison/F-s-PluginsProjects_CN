#include "AeText.h"

#include <cstddef>
#include <cstdint>
#include <type_traits>

#if !defined(_WIN32) || !defined(_WIN64) || !defined(_MSC_VER)
#error AeText V1 is a Windows x64 MSVC ABI.
#endif

static_assert(sizeof(void *) == 8);
static_assert(sizeof(wchar_t) == 2);

static_assert(std::is_standard_layout_v<AeText::TextToken>);
static_assert(std::is_standard_layout_v<AeText::StringTable>);
static_assert(std::is_standard_layout_v<AeText::VariantView>);
static_assert(std::is_standard_layout_v<AeText::CatalogView>);
static_assert(std::is_standard_layout_v<AeText::TextRequest>);
static_assert(std::is_standard_layout_v<AeText::TextResult>);
static_assert(std::is_standard_layout_v<AeText::TextSuite1>);

static_assert(sizeof(AeText::TextToken) == 8);
static_assert(sizeof(AeText::StringTable) == 16);
static_assert(sizeof(AeText::VariantView) == 64);
static_assert(sizeof(AeText::CatalogView) == 24);
static_assert(sizeof(AeText::TextRequest) == 8);
static_assert(sizeof(AeText::TextResult) == 16);
static_assert(sizeof(AeText::TextSuite1) == 16);

static_assert(offsetof(AeText::TextToken, role) == 0);
static_assert(offsetof(AeText::TextToken, index) == 4);
static_assert(offsetof(AeText::StringTable, values) == 0);
static_assert(offsetof(AeText::StringTable, count) == 8);
static_assert(offsetof(AeText::VariantView, struct_size) == 0);
static_assert(offsetof(AeText::VariantView, stable_id_size) == 4);
static_assert(offsetof(AeText::VariantView, stable_id) == 8);
static_assert(offsetof(AeText::VariantView, role_tables) == 16);
static_assert(offsetof(AeText::VariantView, role_table_count) == 24);
static_assert(offsetof(AeText::VariantView, about_utf8) == 32);
static_assert(offsetof(AeText::VariantView, error_utf8) == 48);
static_assert(offsetof(AeText::CatalogView, struct_size) == 0);
static_assert(offsetof(AeText::CatalogView, version) == 4);
static_assert(offsetof(AeText::CatalogView, variants) == 8);
static_assert(offsetof(AeText::CatalogView, variant_count) == 16);
static_assert(offsetof(AeText::CatalogView, fallback_variant_index) == 20);
static_assert(offsetof(AeText::TextRequest, token) == 0);
static_assert(offsetof(AeText::TextResult, legacy) == 0);
static_assert(offsetof(AeText::TextResult, utf8) == 8);
static_assert(offsetof(AeText::TextSuite1, Resolve) == 0);
static_assert(offsetof(AeText::TextSuite1, ShowOptions) == 8);

#pragma warning(push)
#pragma warning(disable: 4324)
struct __declspec(align(16)) Align16Probe {
    char value;
};

struct PackBoundaryProbe {
    char prefix;
    Align16Probe aligned;
};
#pragma warning(pop)

static_assert(offsetof(PackBoundaryProbe, aligned) == 16);

constexpr char kSourceId[] = "source";
constexpr AeText::StringTable kEmptyTable{nullptr, 0};
constexpr AeText::StringTable kRoleTables[AeText::kTextRoleCount]{};
constexpr AeText::VariantView kSourceVariant{
    sizeof(AeText::VariantView),
    sizeof(kSourceId) - 1,
    kSourceId,
    kRoleTables,
    AeText::kTextRoleCount,
    kEmptyTable,
    kEmptyTable,
};
static_assert(kSourceVariant.stable_id_size == 6);

int main()
{
    return kSourceVariant.stable_id[kSourceVariant.stable_id_size] == '\0' ? 0 : 1;
}
