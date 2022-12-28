import subprocess

import pandas as pd


def test_cli_fetch_klines(tmp_path):
    csv_path = tmp_path / "a.csv"
    json_path = tmp_path / "a.json"
    excel_path = tmp_path / "a.xlsx"
    non_support_path = tmp_path / "a.sb"

    cmd = (
        "bh --data-type klines --asset-type spot --symbol BTCUSDT --start 2022-1-2"
        " --end 2022-1-10 --timeframe 15m --tz Asia/Shanghai --output-path {}"
    )
    subprocess.run(cmd.format(csv_path), shell=True, check=True)
    assert csv_path.exists()

    df = pd.read_csv(csv_path, parse_dates=True, index_col=0)
    assert df.index[0].day == 2
    assert df.index[-1].day == 10

    subprocess.run(cmd.format(json_path), shell=True, check=True)
    assert json_path.exists()

    subprocess.run(cmd.format(excel_path), shell=True, check=True)
    assert excel_path.exists()

    subprocess.run(cmd.format(excel_path), shell=True, check=True)
    assert excel_path.exists()

    process = subprocess.run(
        cmd.format(non_support_path),
        shell=True,
        capture_output=True,
        text=True,
    )
    assert process.returncode != 0
    assert "not support extension name: sb" in process.stderr


def test_cli_fetch_agg_trades(tmp_path):
    csv_path = tmp_path / "a.csv"

    cmd = (
        "bh --data-type aggTrades --asset-type spot --symbol ETCBTC --start 2022-1-2"
        " --end '2022-1-4 12:00' --tz Asia/Shanghai --output-path {}"
    )
    subprocess.run(cmd.format(csv_path), shell=True, check=True)
    assert csv_path.exists()

    df = pd.read_csv(csv_path, parse_dates=True, index_col=0)
    assert df.index[0].day == 2
    assert df.index[-1].day == 4
