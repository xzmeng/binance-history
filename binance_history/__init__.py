import sys

from .api import fetch_klines, fetch_agg_trades

if sys.version_info[:2] >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

__version__ = metadata.version(__package__)

del metadata, sys

__all__ = ["fetch_klines", "fetch_agg_trades"]
