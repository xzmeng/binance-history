from importlib import metadata

from .api import fetch_klines, fetch_agg_trades

__version__ = metadata.version(__package__)
del metadata

__all__ = ["fetch_klines", "fetch_agg_trades"]
