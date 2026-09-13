#pragma once

#include "../AeText.h"

#include <cstdint>

namespace AeText::detail {

inline const VariantView *FallbackVariant(const CatalogView &catalog) noexcept
{
	return &catalog.variants[catalog.fallback_variant_index];
}

inline const VariantView *FindVariant(
	const CatalogView &catalog,
	const char *stable_id,
	std::uint32_t stable_id_size) noexcept
{
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

inline const char *LegacyValue(
	const VariantView &variant,
	TextToken token) noexcept
{
	return variant.role_tables[static_cast<std::uint32_t>(token.role)].values[token.index];
}

inline const char *Utf8Value(
	const VariantView &variant,
	TextToken token) noexcept
{
	const StringTable &table = token.role == TextRole::About
		? variant.about_utf8 : variant.error_utf8;
	return table.values[token.index];
}

} // namespace AeText::detail
