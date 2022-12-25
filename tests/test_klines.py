import pendulum
from binance_history.klines import fetch_klines


def test_fetch_klines_1min():
    symbol = 'BTC/USDT'
    kind = 'spot'
    timeframe = '1min'
    start = pendulum.datetime(2022, 12, 1, 2, 3, tz='Asia/Shanghai')
    end = pendulum.datetime(2022, 12, 2, 3, 4, tz='Asia/Shanghai')

    klines = fetch_klines(
        symbol=symbol,
        kind=kind,
        timeframe=timeframe,
        start=start,
        end=end,
    )

    assert klines[0]['open_datetime'] == pendulum.datetime(2022, 12, 1, 2, 3, tz='Asia/Shanghai')
    assert klines[0]['close_datetime'] == pendulum.datetime(2022, 12, 1, 2, 3, 59, 999, tz='Asia/Shanghai')

    assert klines[-1]['open_datetime'] == pendulum.datetime(2022, 12, 2, 3, 4, tz='Asia/Shanghai')
    assert klines[-1]['close_datetime'] == pendulum.datetime(2022, 12, 2, 3, 4, 59, 999, tz='Asia/Shanghai')

    assert (klines[-1]['open_datetime'] - klines[0]['open_datetime']).in_minutes() == len(klines)


def test_fetch_klines_15min():
    symbol = 'BTC/USDT'
    kind = 'spot'
    timeframe = '15min'
    start = pendulum.datetime(2022, 12, 1, 2, 3, tz='Asia/Shanghai')
    end = pendulum.datetime(2022, 12, 2, 3, 4, tz='Asia/Shanghai')

    klines = fetch_klines(
        symbol=symbol,
        kind=kind,
        timeframe=timeframe,
        start=start,
        end=end,
    )

    assert klines[0]['open_datetime'] == pendulum.datetime(2022, 12, 1, 2, 15, tz='Asia/Shanghai')
    assert klines[0]['close_datetime'] == pendulum.datetime(2022, 12, 1, 2, 29, 59, 999, tz='Asia/Shanghai')

    assert klines[-1]['open_datetime'] == pendulum.datetime(2022, 12, 2, 3, 0, tz='Asia/Shanghai')
    assert klines[-1]['close_datetime'] == pendulum.datetime(2022, 12, 2, 3, 15, 59, 999, tz='Asia/Shanghai')

    assert (klines[-1]['open_datetime'] - klines[0]['open_datetime']).in_minutes() // 15 == len(klines)
