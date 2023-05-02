import sys

from .api import fetch_klines, fetch_agg_trades, fetch_data

from importlib import metadata

__version__ = metadata.version(__package__)

del metadata, sys

__all__ = ["fetch_klines", "fetch_agg_trades", "fetch_data"]
