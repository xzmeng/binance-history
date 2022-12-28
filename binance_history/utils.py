import io
import os
import os.path
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import httpx
import pandas as pd
from pandas import Timestamp, DataFrame

from . import config


def gen_data_url(
    data_type: str,
    asset_type: str,
    freq: str,
    symbol: str,
    dt: Timestamp,
    timeframe: str | None = None,
):
    url: str
    date_str: str

    if freq == "monthly":
        date_str = dt.strftime("%Y-%m")
    elif freq == "daily":
        date_str = dt.strftime("%Y-%m-%d")
    else:
        raise ValueError(f"freq must be 'monthly' or 'daily', but got '{freq}'")

    if data_type == "klines":
        if timeframe is None:
            raise ValueError("'timeframe' must not be None when data_type is 'klines'")
        url = (
            f"https://data.binance.vision/data/{asset_type}/{freq}/{data_type}/{symbol}/{timeframe}"
            f"/{symbol}-{timeframe}-{date_str}.zip"
        )
    elif data_type == "aggTrades":
        url = (
            f"https://data.binance.vision/data/{asset_type}/{freq}/{data_type}/{symbol}"
            f"/{symbol}-{data_type}-{date_str}.zip"
        )
    else:
        raise ValueError(f"data_type must be 'klines', but got '{data_type}'")
    return url


def gen_dates(
    data_type: str,
    asset_type: str,
    symbol: str,
    start: Timestamp,
    end: Timestamp,
    timeframe: str | None = None,
):
    assert start.tz is None and end.tz is None

    if start > end:
        raise ValueError("start cannot be greater than end")

    months = pd.date_range(
        Timestamp(start.year, start.month, 1),
        end,
        freq="MS",
    ).to_list()

    assert len(months) > 0

    last_month_url = gen_data_url(
        data_type, asset_type, "monthly", symbol, months[-1], timeframe=timeframe
    )

    resp = httpx.head(last_month_url)

    assert resp.status_code in [404, 200], f"wrong status code: {resp.status_code}"

    if resp.status_code == 404:
        months.pop()
        days = pd.date_range(
            Timestamp(end.year, end.month, 1),
            end,
            freq="D",
        ).to_list()
    elif resp.status_code == 200:
        days = []

    return months, days


def get_data(
    data_type: str,
    asset_type: str,
    freq: str,
    symbol: str,
    dt: Timestamp,
    data_tz: str,
    timeframe: str | None = None,
) -> DataFrame:
    if data_type == "klines":
        assert timeframe is not None

    url = gen_data_url(data_type, asset_type, freq, symbol, dt, timeframe)

    df = load_data_from_disk(url)
    if df is None:
        df = download_data(data_type, data_tz, url)
        save_data_to_disk(url, df)
    return df


def download_data(data_type: str, data_tz: str, url: str) -> DataFrame:
    assert data_type in ["klines", "aggTrades"]
    if data_type == "klines":
        return download_klines(data_tz, url)
    elif data_type == "aggTrades":
        return download_agg_trades(data_tz, url)


def download_klines(data_tz, url) -> DataFrame:
    resp = httpx.get(url)
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zipf:
        csv_name = zipf.namelist()[0]
        with zipf.open(csv_name, "r") as csvfile:
            df = pd.read_csv(
                csvfile,
                usecols=range(9),
                header=None,
                names=[
                    "open_ms",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "close_ms",
                    "quote_volume",
                    "trades",
                ],
            )
            df["open_datetime"] = pd.to_datetime(
                df.open_ms, unit="ms", utc=True
            ).dt.tz_convert(data_tz)
            df["close_datetime"] = pd.to_datetime(
                df.close_ms, unit="ms", utc=True
            ).dt.tz_convert(data_tz)
            del df["open_ms"]
            del df["close_ms"]
            df.set_index("open_datetime", inplace=True)
    return df


def download_agg_trades(data_tz, url) -> DataFrame:
    resp = httpx.get(url)
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zipf:
        csv_name = zipf.namelist()[0]
        with zipf.open(csv_name, "r") as csvfile:
            df = pd.read_csv(
                csvfile,
                usecols=[1, 2, 5, 6],
                header=None,
                names=["price", "quantity", "timestamp", "is_buyer_maker"],
            )
            df["datetime"] = pd.to_datetime(
                df.timestamp, unit="ms", utc=True
            ).dt.tz_convert(data_tz)
            del df["timestamp"]
            df.set_index("datetime", inplace=True)
    return df


def get_local_data_path(url: str) -> Path:
    path = urlparse(url).path
    return config.CACHE_DIR / path[1:]


def save_data_to_disk(url: str, df: DataFrame) -> None:
    path = get_local_data_path(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_pickle(path)


def load_data_from_disk(url: str) -> DataFrame | None:
    path = get_local_data_path(url)
    if os.path.exists(path):
        return pd.read_pickle(path)
    else:
        return None
