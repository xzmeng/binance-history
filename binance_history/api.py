from datetime import datetime

import pandas as pd
import pendulum
from pandas import DataFrame

from .utils import gen_dates, get_data, unify_datetime
from typing import Optional, Union


def fetch_klines(
    symbol: str,
    start: Union[str, datetime],
    end: Union[str, datetime],
    timeframe: str = "1m",
    asset_type: str = "spot",
    tz: Optional[str] = None,
) -> DataFrame:
    """convinience function by calling ``fetch_data"""

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
    symbol: str,
    start: Union[str, datetime],
    end: Union[str, datetime],
    asset_type: str = "spot",
    tz: Optional[str] = None,
) -> DataFrame:
    """convinience function by calling ``fetch_data"""

    return fetch_data(
        data_type="aggTrades",
        asset_type=asset_type,
        symbol=symbol,
        start=start,
        end=end,
        tz=tz,
    )


def fetch_data(
    symbol: str,
    asset_type: str,
    data_type: str,
    start: datetime,
    end: datetime,
    tz: Optional[str] = None,
    timeframe: Optional[str] = None,
) -> DataFrame:
    """
    :param symbol: The binance market pair name. e.g. ``'BTCUSDT'``.
    :param start:  The start datetime of requested data. If it's an instance of ``datetime.datetime``,
    :param asset_type: The asset type of requested data. It must be one of ``'spot'``, ``'futures/um'``, ``'futures/cm'``.
    :param data_type: The type of requested data. It must be one of ``'klines'``, ``'agg_trades'``.
        it's timezone is ignored. If it's a ``str``, it should be parsed by
        `dateutil <https://github.com/dateutil/dateutil>`_, e.g. ``"2022-1-1 8:10"``.
    :param end:  The end datetime of requested data. If it's an instance of ``datetime.datetime``,
        it's timezone is ignored. If it's a ``str``, it should be parsed by
        `dateutil <https://github.com/dateutil/dateutil>`_, e.g. ``"2022-1-2 8:10"``.
    :param tz: Timezone of ``start``, ``end``, and the open/close datetime of the returned dataframe.
        It should be a time zone name of `tz database <https://en.wikipedia.org/wiki/Tz_database>`_, e.g. "Asia/Shanghai".
        Your can find a full list of available time zone names in
        `List of tz database time zones <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List>`_.
    :param timeframe: The kline interval. e.g. "1m". see ``binance_history.constants.TIMEFRAMES``
        to see the full list of available intervals.
    :return: A pandas dataframe with columns `open`, `high`, `low`, `close`, `volume`, `trades`, `close_datetime`.
        the dataframe's index is the open datetime of klines, the timezone of the datetime is set by ``tz``,
        if it is None, your local timezone will be used.
    """
    if tz is None:
        tz = pendulum.local_timezone().name

    start, end = unify_datetime(start), unify_datetime(end)

    start, end = pd.Timestamp(start, tz=tz), pd.Timestamp(
        end, tz=tz
    )

    symbol = symbol.upper().replace("/", "")

    months, days = gen_dates(
        data_type,
        asset_type,
        symbol,
        start.tz_convert(None),
        end.tz_convert(None),
        timeframe=timeframe,
    )
    monthly_dfs = [
        get_data(
            data_type, asset_type, "monthly", symbol, dt, tz, timeframe
        )
        for dt in months
    ]
    daily_dfs = [
        get_data(
            data_type, asset_type, "daily", symbol, dt, tz, timeframe
        )
        for dt in days
    ]
    df = pd.concat(monthly_dfs + daily_dfs)
    return df.loc[start:end]
