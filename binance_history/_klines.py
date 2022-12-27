import pandas as pd
from pandas import Timestamp, DataFrame
from ._exceptions import MissingTimeZone
from ._utils import gen_dates, get_data


def fetch_klines(
    asset_type: str,
    symbol: str,
    timeframe: str,
    start: str | Timestamp,
    end: str | Timestamp,
    tz: str | None = None,
) -> DataFrame:
    """
    if `start` or `end` is Timestamp, its timezone take the higher precedence
    """
    data_tz: str | None
    start, end = Timestamp(start), Timestamp(end)
    if not start.tz or not end.tz:
        if tz is None:
            raise MissingTimeZone
        if not start.tz:
            start = start.tz_localize(tz)
        if not end.tz:
            end = end.tz_localize(tz)
    data_tz = start.tz

    months, days = gen_dates(
        "klines",
        asset_type,
        symbol,
        start.tz_convert(None),
        end.tz_convert(None),
        timeframe=timeframe,
    )
    monthly_dfs = [
        get_data("klines", asset_type, "monthly", symbol, dt, data_tz, timeframe)
        for dt in months
    ]
    daily_dfs = [
        get_data("klines", asset_type, "daily", symbol, dt, data_tz, timeframe)
        for dt in days
    ]
    df = pd.concat(monthly_dfs + daily_dfs)
    return df.loc[start:end]
