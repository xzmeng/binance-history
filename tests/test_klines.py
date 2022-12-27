import pytest
from binance_history import fetch_klines
from pandas import Timestamp, Timedelta
from binance_history._exceptions import MissingTimeZone
from binance_history import config


def test_fetch_klines_1m_one_month(tmp_path):
    config.CACHE_DIR = tmp_path
    asset_type = "spot"
    symbol = "BTCUSDT"
    start = "2022-1-2 5:29"
    end = "2022-1-5 11:31"
    tz = "Asia/Shanghai"

    klines = fetch_klines(asset_type, symbol, "1m", start, end, tz)

    assert klines.index[0] == Timestamp(start, tz=tz)
    assert klines.close_datetime[0] == Timestamp("2022-1-2 5:29:59.999", tz=tz)
    assert klines.index[-1] == Timestamp(end, tz=tz)
    assert klines.close_datetime[-1] == Timestamp("2022-1-5 11:31:59.999", tz=tz)


def test_fetch_klines_1m_many_months():
    asset_type = "spot"
    symbol = "BTCUSDT"
    start = "2022-1-1 5:29"
    end = "2022-2-3 11:31"
    tz = "Asia/Shanghai"

    klines = fetch_klines(asset_type, symbol, "1m", start, end, tz)

    assert klines.index[0] == Timestamp(start, tz=tz)
    assert klines.close_datetime[0] == Timestamp("2022-1-1 5:29:59.999", tz=tz)
    assert klines.index[-1] == Timestamp(end, tz=tz)
    assert klines.close_datetime[-1] == Timestamp("2022-2-3 11:31:59.999", tz=tz)


def test_fetch_klines_15m_many_months():
    asset_type = "spot"
    symbol = "BTCUSDT"
    start = "2022-1-1 5:29"
    end = "2022-2-3 11:31"
    tz = "Asia/Shanghai"

    klines = fetch_klines(asset_type, symbol, "15m", start, end, tz)

    assert klines.index[0] == Timestamp("2022-1-1 5:30", tz=tz)
    assert klines.close_datetime[0] == Timestamp("2022-1-1 5:44:59.999", tz=tz)
    assert klines.index[-1] == Timestamp("2022-2-3 11:30", tz=tz)
    assert klines.close_datetime[-1] == Timestamp("2022-2-3 11:44:59.999", tz=tz)


def test_fetch_klines_1h_this_month():
    asset_type = "spot"
    symbol = "BTCUSDT"
    start = "2022-11-2 5:29"
    end = Timestamp.now() - Timedelta(days=2)
    tz = "Asia/Shanghai"

    klines = fetch_klines(asset_type, symbol, "1h", start, end, tz)

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


def test_fetch_klines_missing_timezone():
    asset_type = "spot"
    symbol = "BTCUSDT"
    start = "2022-1-2 5:29"
    end = "2022-1-5 11:31"
    tz = "Asia/Shanghai"

    fetch_klines(
        asset_type,
        symbol,
        "1m",
        Timestamp(start, tz=tz),
        Timestamp(end, tz=tz),
        tz=None,
    )

    fetch_klines(
        asset_type,
        symbol,
        "1m",
        Timestamp(start, tz=None),
        Timestamp(end, tz=None),
        tz=tz,
    )

    with pytest.raises(MissingTimeZone):
        fetch_klines(asset_type, symbol, "1m", start, end, tz=None)
