import subprocess

import pandas as pd


def test_cli(tmp_path):
    filepath = tmp_path / "BTCUSDT-klines.csv"
    cmd = (
        "bh --data-type klines --asset-type spot --symbol BTCUSDT --start 2022-1-2"
        f" --end 2022-1-10 --timeframe 15m --tz Asia/Shanghai --output-path {filepath}"
    )
    subprocess.run(cmd, shell=True, check=True)
    assert filepath.exists()

    df = pd.read_csv(filepath, parse_dates=True, index_col=0)
    assert df.index[0].day == 2
    assert df.index[-1].day == 10
