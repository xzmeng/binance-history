import pytest
from pandas import Timestamp, Timedelta

from binance_history.utils import gen_data_url, gen_dates


def test_gen_data_url():
    assert (
        gen_data_url(
            "klines", "spot", "monthly", "BTCUSDT", Timestamp("2022-11"), timeframe="1m"
        )
        == "https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-2022-11.zip"
    )
    assert (
        gen_data_url(
            "klines",
            "spot",
            "daily",
            "BTCUSDT",
            Timestamp("2022-11-01"),
            timeframe="1m",
        )
        == "https://data.binance.vision/data/spot/daily/klines/BTCUSDT/1m/BTCUSDT-1m-2022-11-01.zip"
    )
    assert (
        gen_data_url("aggTrades", "spot", "monthly", "BTCUSDT", Timestamp("2022-11"))
        == "https://data.binance.vision/data/spot/monthly/aggTrades/BTCUSDT/BTCUSDT-aggTrades-2022-11.zip"
    )
    with pytest.raises(ValueError):
        gen_data_url("aggTrades", "spot", "annual", "BTCUSDT", Timestamp("2022-11"))
    with pytest.raises(ValueError):
        gen_data_url("klines", "spot", "daily", "BTCUSDT", Timestamp("2022-11"))
    with pytest.raises(ValueError):
        gen_data_url("trades", "spot", "daily", "BTCUSDT", Timestamp("2022-11"))


def test_gen_dates():
    months, days = gen_dates(
        "klines", "spot", "BTCUSDT", Timestamp("2022-2-10"), Timestamp("2022-3-5"), "1m"
    )
    assert months == [Timestamp("2022-2"), Timestamp("2022-3")]
    assert days == []

    months, days = gen_dates(
        "klines", "spot", "BTCUSDT", Timestamp("2022-1-31"), Timestamp("2022-3-5"), "1m"
    )
    assert months == [Timestamp("2022-1"), Timestamp("2022-2"), Timestamp("2022-3")]

    start = Timestamp("2022-2-1")
    end = Timestamp.today() - Timedelta(days=1)
    months, days = gen_dates(
        "klines",
        "spot",
        "BTCUSDT",
        start,
        end,
        "1m",
    )
    assert months[-1].month % 12 == end.month - 1
    assert len(days) == end.day

    with pytest.raises(ValueError):
        gen_dates(
            "klines",
            "spot",
            "BTCUSDT",
            Timestamp("2022-1-1"),
            Timestamp("2021-12-1"),
            "1m",
        )
