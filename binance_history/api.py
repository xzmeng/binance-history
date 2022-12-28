import pandas as pd
import pendulum
from pandas import Timestamp, DataFrame

from .utils import gen_dates, get_data


def fetch_klines(
    symbol: str,
    start: str | Timestamp,
    end: str | Timestamp,
    timeframe: str = "1m",
    asset_type: str = "spot",
    tz: str | None = None,
) -> DataFrame:
    return fetch_data(
        data_type="klines",
        asset_type=asset_type,
        symbol=symbol,
        start=start,
        end=end,
        timeframe=timeframe,
        tz=tz,
    )


def fetch_agg_trades(
    asset_type: str,
    symbol: str,
    start: str | Timestamp,
    end: str | Timestamp,
    tz: str | None = None,
) -> DataFrame:
    return fetch_data(
        data_type="aggTrades",
        asset_type=asset_type,
        symbol=symbol,
        start=start,
        end=end,
        tz=tz,
    )


def fetch_data(
    data_type: str,
    asset_type: str,
    symbol: str,
    start: str | Timestamp,
    end: str | Timestamp,
    tz: str | None = None,
    timeframe: str | None = None,
) -> DataFrame:
    """
    if `start` or `end` is Timestamp, its timezone take the higher precedence
    """
    if tz is None:
        tz = pendulum.local_timezone().name
    start, end = Timestamp(start), Timestamp(end)
    if not start.tz or not end.tz:
        if not start.tz:
            start = start.tz_localize(tz)
        if not end.tz:
            end = end.tz_localize(tz)
    assert start.tz == end.tz
    data_tz = start.timetz().tzname()

    months, days = gen_dates(
        data_type,
        asset_type,
        symbol,
        start.tz_convert(None),
        end.tz_convert(None),
        timeframe=timeframe,
    )
    monthly_dfs = [
        get_data(data_type, asset_type, "monthly", symbol, dt, data_tz, timeframe)
        for dt in months
    ]
    daily_dfs = [
        get_data(data_type, asset_type, "daily", symbol, dt, data_tz, timeframe)
        for dt in days
    ]
    df = pd.concat(monthly_dfs + daily_dfs)
    return df.loc[start:end]
