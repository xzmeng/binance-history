import datetime
import io
import os
import os.path
import zipfile
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

import httpx
import pandas as pd
import pendulum
from pandas import Timestamp, DataFrame

from . import config
from .exceptions import NetworkError, DataNotFound


def gen_data_url(
    data_type: str,
    asset_type: str,
    freq: str,
    symbol: str,
    dt: Timestamp,
    timeframe: Optional[str] = None,
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


def unify_datetime(input: Union[str, datetime.datetime]) -> datetime.datetime:
    if isinstance(input, str):
        return pendulum.parse(input, strict=False).replace(tzinfo=None)
    elif isinstance(input, datetime.datetime):
        return input.replace(tzinfo=None)
    else:
        raise TypeError(input)


def exists_month(month_url):
    try:
        resp = httpx.head(month_url)
    except (httpx.TimeoutException, httpx.NetworkError) as e:
        raise NetworkError(e)

    if resp.status_code == 200:
        return True
    elif resp.status_code == 404:
        return False
    else:
        raise NetworkError(resp.status_code)


def gen_dates(
    data_type: str,
    asset_type: str,
    symbol: str,
    start: Timestamp,
    end: Timestamp,
    timeframe: Optional[str] = None,
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

    if not exists_month(last_month_url):
        daily_month = months.pop()
        if len(months) > 1:
            second_last_month_url = gen_data_url(
                data_type,
                asset_type,
                "monthly",
                symbol,
                months[-1],
                timeframe=timeframe,
            )
            if not exists_month(second_last_month_url):
                daily_month = months.pop()

        days = pd.date_range(
            Timestamp(daily_month.year, daily_month.month, 1),
            end,
            freq="D",
        ).to_list()
    else:
        days = []

    return months, days


def get_data(
    data_type: str,
    asset_type: str,
    freq: str,
    symbol: str,
    dt: Timestamp,
    data_tz: str,
    timeframe: Optional[str] = None,
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

    try:
        resp = httpx.get(url)
    except (httpx.TimeoutException, httpx.NetworkError) as e:
        raise NetworkError(e)

    if resp.status_code == 200:
        pass
    elif resp.status_code == 404:
        raise DataNotFound(url)
    else:
        raise NetworkError(url)

    if data_type == "klines":
        return load_klines(data_tz, resp.content)
    elif data_type == "aggTrades":
        return load_agg_trades(data_tz, resp.content)


def load_klines(data_tz: str, content: bytes) -> DataFrame:
    with zipfile.ZipFile(io.BytesIO(content)) as zipf:
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


def load_agg_trades(data_tz: str, content: bytes) -> DataFrame:
    with zipfile.ZipFile(io.BytesIO(content)) as zipf:
        csv_name = zipf.namelist()[0]
        with zipf.open(csv_name, "r") as csvfile:
            df = pd.read_csv(
                csvfile,
                header=0,
                usecols=[1, 2, 5, 6],
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


def load_data_from_disk(url: str) -> Union[DataFrame, None]:
    path = get_local_data_path(url)
    if os.path.exists(path):
        return pd.read_pickle(path)
    else:
        return None
