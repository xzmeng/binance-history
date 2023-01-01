import datetime

import pendulum
import pytest
from pandas import Timestamp, Timedelta

from binance_history import fetch_klines, fetch_agg_trades


@pytest.mark.parametrize(
    ("symbol", "asset_type"),
    [
        ("BTCUSDT", "spot"),
        ("BTCUSDT", "futures/um"),
        ("BTCUSD_PERP", "futures/cm"),
    ],
)
@pytest.mark.parametrize(
    ("start", "end", "tz"),
    [
        ("2022-1-2", "2022-1-20", "Asia/Shanghai"),
        (
            pendulum.datetime(2022, 1, 2, tz="Europe/Paris"),
            pendulum.datetime(2022, 1, 20, tz="Europe/Paris"),
            "Asia/Shanghai",
        ),
        (
            datetime.datetime(2022, 1, 2),
            datetime.datetime(2022, 1, 20),
            "Asia/Shanghai",
        ),
    ],
)
@pytest.mark.parametrize("timeframe", ["1m"])
def test_fetch_klines_1m_one_month(symbol, start, end, timeframe, asset_type, tz):
    klines = fetch_klines(
        symbol=symbol,
        start=start,
        end=end,
        timeframe=timeframe,
        asset_type=asset_type,
        tz=tz,
    )

    first_opentime = Timestamp("2022-1-2", tz="Asia/Shanghai")
    first_closetime = Timestamp("2022-1-2 0:0:59.999", tz="Asia/Shanghai")
    last_opentime = Timestamp("2022-1-20", tz="Asia/Shanghai")
    last_closetime = Timestamp("2022-1-20 0:0:59.999", tz="Asia/Shanghai")

    assert klines.index[0] == first_opentime
    assert klines.close_datetime[0] == first_closetime
    assert klines.index[-1] == last_opentime
    assert klines.close_datetime[-1] == last_closetime


def test_fetch_klines_1m_many_months():
    symbol = "BTCUSDT"
    start = "2022-1-1 5:29"
    end = "2022-2-3 11:31"
    tz = "Asia/Shanghai"

    klines = fetch_klines(
        symbol=symbol,
        start=start,
        end=end,
        tz=tz,
    )

    assert klines.index[0] == Timestamp(start, tz=tz)
    assert klines.close_datetime[0] == Timestamp("2022-1-1 5:29:59.999", tz=tz)
    assert klines.index[-1] == Timestamp(end, tz=tz)
    assert klines.close_datetime[-1] == Timestamp("2022-2-3 11:31:59.999", tz=tz)


def test_fetch_klines_15m_many_months():
    symbol = "BTCUSDT"
    start = "2022-1-1 5:29"
    end = "2022-2-3 11:31"
    tz = "Asia/Shanghai"

    klines = fetch_klines(
        symbol=symbol,
        start=start,
        end=end,
        timeframe="15m",
        tz=tz,
    )

    assert klines.index[0] == Timestamp("2022-1-1 5:30", tz=tz)
    assert klines.close_datetime[0] == Timestamp("2022-1-1 5:44:59.999", tz=tz)
    assert klines.index[-1] == Timestamp("2022-2-3 11:30", tz=tz)
    assert klines.close_datetime[-1] == Timestamp("2022-2-3 11:44:59.999", tz=tz)


def test_fetch_klines_1h_recent_days():
    symbol = "BTCUSDT"
    start = Timestamp("2022-11-2 5:29")
    end = Timestamp.now() - Timedelta(days=3)
    tz = "Asia/Shanghai"

    klines = fetch_klines(
        symbol=symbol,
        start=start,
        end=end,
        timeframe="1h",
        tz=tz,
    )

    assert klines.index[0] == Timestamp("2022-11-2 6:00", tz=tz)
    assert klines.close_datetime[0] == Timestamp("2022-11-2 6:59:59.999", tz=tz)
    assert klines.index[-1] == Timestamp(
        year=end.year, month=end.month, day=end.day, hour=end.hour, tz=tz
    )
    assert klines.close_datetime[-1] == Timestamp(
        year=end.year,
        month=end.month,
        day=end.day,
        hour=end.hour,
        minute=59,
        second=59,
        microsecond=999000,
        tz=tz,
    )


@pytest.mark.parametrize(
    ("start", "end", "tz"),
    [
        ("2022-10-2", "2022-10-19 23:59:59", "Asia/Shanghai"),
    ],
)
@pytest.mark.parametrize(
    ("symbol", "asset_type"), [("ETCBTC", "spot"), ("LTCBUSD", "futures/um")]
)
def test_fetch_agg_trades_one_month(symbol, start, end, tz, asset_type):
    agg_trades = fetch_agg_trades(symbol, start, end, asset_type, tz)
    assert agg_trades.index[0].day == 2
    assert agg_trades.index[-1].day == 19


def test_wrong_datetime_type():
    with pytest.raises(TypeError):
        fetch_klines("btcusdt", 3, 4)
