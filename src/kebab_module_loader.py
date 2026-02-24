"""Utility to load Python modules with kebab-case filenames via importlib."""

import importlib.util
import sys
from pathlib import Path


def load_kebab_module(kebab_path: str | Path, alias: str | None = None):
    """Load a kebab-case .py file as a Python module.

    Args:
        kebab_path: Absolute or relative path to the .py file.
        alias: Optional module name to register in sys.modules.
                Defaults to the stem with hyphens replaced by underscores.

    Returns:
        The loaded module object.
    """
    path = Path(kebab_path).resolve()
    module_name = alias or path.stem.replace("-", "_")

    # Return cached module if already loaded
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


# ── Convenience pre-loaders for data/ modules ─────────────────────────────────

_SRC = Path(__file__).parent


def load_market_data_schemas():
    """Load src/data/market-data-schemas.py."""
    return load_kebab_module(_SRC / "data" / "market-data-schemas.py",
                             alias="market_data_schemas")


def load_clickhouse_client():
    """Load src/storage/clickhouse-client.py."""
    return load_kebab_module(_SRC / "storage" / "clickhouse-client.py",
                             alias="clickhouse_client")


def load_clickhouse_schemas():
    """Load src/storage/clickhouse-schemas.py."""
    return load_kebab_module(_SRC / "storage" / "clickhouse-schemas.py",
                             alias="clickhouse_schemas")
