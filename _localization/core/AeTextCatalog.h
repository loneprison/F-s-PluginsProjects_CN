#pragma once

#include "../AeText.h"

#include <cstddef>
#include <cstdint>

namespace AeText::detail {

inline constexpr bool ValidRole(TextRole role) noexcept
{
	return static_cast<std::uint32_t>(role) < kTextRoleCount;
}

inline constexpr bool ValidStringTable(const StringTable &table) noexcept
{
	return (table.count == 0 && table.values == nullptr) ||
		(table.count > 0 && table.values != nullptr);
}

inline bool ValidStableId(const VariantView &variant) noexcept
{
	if (!variant.stable_id || variant.stable_id_size == 0) {
		return false;
	}
	for (std::uint32_t index = 0; index < variant.stable_id_size; ++index) {
		const auto value = static_cast<unsigned char>(variant.stable_id[index]);
		if (value < 0x21 || value > 0x7e) {
			return false;
		}
	}
	return true;
}

inline bool ValidVariant(const VariantView &variant) noexcept
{
	if (variant.struct_size != sizeof(VariantView) ||
		!ValidStableId(variant) ||
		!variant.role_tables ||
		variant.role_table_count != kTextRoleCount ||
		!ValidStringTable(variant.about_utf8) ||
		!ValidStringTable(variant.error_utf8)) {
		return false;
	}
	for (std::uint32_t role = 0; role < kTextRoleCount; ++role) {
		if (!ValidStringTable(variant.role_tables[role])) {
			return false;
		}
	}
	return true;
}

inline bool SameStableId(
	const VariantView &left,
	const VariantView &right) noexcept
{
	if (left.stable_id_size != right.stable_id_size) {
		return false;
	}
	for (std::uint32_t index = 0; index < left.stable_id_size; ++index) {
		if (left.stable_id[index] != right.stable_id[index]) {
			return false;
		}
	}
	return true;
}

inline bool ValidCatalog(const CatalogView &catalog) noexcept
{
	if (catalog.struct_size != sizeof(CatalogView) ||
		catalog.version != kCatalogVersion ||
		!catalog.variants ||
		catalog.variant_count == 0 ||
		catalog.fallback_variant_index >= catalog.variant_count) {
		return false;
	}
	for (std::uint32_t index = 0; index < catalog.variant_count; ++index) {
		if (!ValidVariant(catalog.variants[index])) {
			return false;
		}
		if (index > 0) {
			const VariantView &first = catalog.variants[0];
			const VariantView &current = catalog.variants[index];
			for (std::uint32_t role = 0; role < kTextRoleCount; ++role) {
				if (first.role_tables[role].count != current.role_tables[role].count) {
					return false;
				}
			}
			if (first.about_utf8.count != current.about_utf8.count ||
				first.error_utf8.count != current.error_utf8.count) {
				return false;
			}
		}
		for (std::uint32_t previous = 0; previous < index; ++previous) {
			if (SameStableId(catalog.variants[index], catalog.variants[previous])) {
				return false;
			}
		}
	}
	return true;
}

inline const VariantView *FallbackVariant(const CatalogView &catalog) noexcept
{
	return ValidCatalog(catalog)
		? &catalog.variants[catalog.fallback_variant_index]
		: nullptr;
}

inline const VariantView *FindVariant(
	const CatalogView &catalog,
	const char *stable_id,
	std::uint32_t stable_id_size) noexcept
{
	if (!ValidCatalog(catalog) || !stable_id || stable_id_size == 0) {
		return nullptr;
	}
	for (std::uint32_t index = 0; index < catalog.variant_count; ++index) {
		const VariantView &variant = catalog.variants[index];
		if (variant.stable_id_size != stable_id_size) {
			continue;
		}
		bool equal = true;
		for (std::uint32_t character = 0; character < stable_id_size; ++character) {
			if (variant.stable_id[character] != stable_id[character]) {
				equal = false;
				break;
			}
		}
		if (equal) {
			return &variant;
		}
	}
	return nullptr;
}

inline const StringTable *RoleTable(
	const VariantView &variant,
	TextRole role) noexcept
{
	return ValidRole(role) && ValidVariant(variant)
		? &variant.role_tables[static_cast<std::uint32_t>(role)]
		: nullptr;
}

inline const char *TableValue(
	const StringTable *table,
	std::uint32_t index) noexcept
{
	return table && ValidStringTable(*table) && index < table->count
		? table->values[index]
		: nullptr;
}

inline const char *LegacyValue(
	const VariantView &variant,
	TextToken token) noexcept
{
	return TableValue(RoleTable(variant, token.role), token.index);
}

inline const char *Utf8Value(
	const VariantView &variant,
	TextToken token) noexcept
{
	if (token.role == TextRole::About) {
		return TableValue(&variant.about_utf8, token.index);
	}
	if (token.role == TextRole::Error) {
		return TableValue(&variant.error_utf8, token.index);
	}
	return nullptr;
}

} // namespace AeText::detail
