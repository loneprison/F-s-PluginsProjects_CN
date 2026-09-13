"""Public source-scanner facade for AeText tooling."""

from .scanner_treesitter import scan_sources_treesitter

scan_sources = scan_sources_treesitter

__all__ = ["scan_sources"]
