import sys

import click
from loguru import logger

from .api import fetch_data

TIMEFRAMES = [
    "1s",
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
    "1M",
]


@click.command()
@click.option(
    "--data-type",
    type=click.Choice(["klines", "aggTrades"]),
    default="klines",
    help="choose klines or aggTrades to download, default to 'klines'",
)
@click.option(
    "--asset-type",
    type=click.Choice(["spot", "futures-usd", "futures-coin"]),
    default="spot",
    help="choose spot or futures data, default to 'spot'",
)
@click.option(
    "--symbol", required=True, help="The binance market pair name, e.g. BTCUSDT"
)
@click.option(
    "--timeframe",
    default="15m",
    type=click.Choice(TIMEFRAMES),
    help="The timeframe of klines, default to '15m', can be omitted if --data-type is not 'klines'",
)
@click.option("--start", required=True, help="The start datetime, e.g. '2022-1-2 5:20'")
@click.option("--end", required=True, help="The end datetime, e.g. '2022-1-25")
@click.option(
    "--tz", default="Asia/Shanghai", help="The timezone, default to 'Asia/Shanghai'"
)
@click.option(
    "--output-path",
    help="The path you want to save the downloaded data, support format: [csv, json, xlsx], e.g. a.xlsx",
    required=True,
)
@logger.catch(onerror=lambda _: sys.exit(1))
def main(data_type, asset_type, symbol, timeframe, start, end, tz, output_path):
    df = fetch_data(
        data_type=data_type,
        asset_type=asset_type,
        symbol=symbol,
        timeframe=timeframe,
        start=start,
        end=end,
        tz=tz,
    )
    ext = output_path.split(".")[-1]

    if ext == "csv":
        df.to_csv(output_path)
    elif ext == "json":
        df.to_json(output_path, orient="records")
    elif ext == "xlsx":
        df.index = df.index.tz_convert(None)
        if "close_datetime" in df.columns:
            df["close_datetime"] = df.close_datetime.dt.tz_convert(None)
        df.to_excel(output_path)
    else:
        raise ValueError(f"not support extension name: {ext}")
