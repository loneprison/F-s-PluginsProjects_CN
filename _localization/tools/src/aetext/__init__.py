"""Narrow build-time tooling for the AeText source-derived catalog contract."""

from .migration import (
    compare_legacy_baseline,
    materialize_legacy_migration,
    plan_legacy_migration,
)
from .scanner import scan_sources
from .schema import (
    synchronize_effect_catalog,
    validate_effect_catalog,
    validate_family_definition,
)

__all__ = [
    "compare_legacy_baseline",
    "materialize_legacy_migration",
    "plan_legacy_migration",
    "scan_sources",
    "synchronize_effect_catalog",
    "validate_effect_catalog",
    "validate_family_definition",
]
