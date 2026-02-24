"""Re-export shim: delegates to the canonical market-data-schemas.py (kebab-case).

This file exists only for tools/linters that cannot handle kebab-case imports.
All actual implementation lives in src/data/market-data-schemas.py.
"""
from src.kebab_module_loader import load_market_data_schemas as _load

_mod = _load()

AssetClass = _mod.AssetClass
TickData = _mod.TickData
OHLCVBar = _mod.OHLCVBar
FinancialReport = _mod.FinancialReport

__all__ = ["AssetClass", "TickData", "OHLCVBar", "FinancialReport"]
