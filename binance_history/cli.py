import sys

import click
from loguru import logger

from .api import fetch_data
from .constants import TIMEFRAMES
from .utils import unify_datetime


@click.command()
@click.option(
    "--symbol", required=True, help="The binance market pair name, e.g. BTCUSDT"
)
@click.option("--start", required=True, help="The start datetime, e.g. '2022-1-2 1:10'")
@click.option("--end", required=True, help="The end datetime, e.g. '2022-1-25 2:20")
@click.option(
    "--data-type",
    type=click.Choice(["klines", "aggTrades"]),
    default="klines",
    help="choose klines or aggTrades to download, default to 'klines'",
)
@click.option(
    "--asset-type",
    type=click.Choice(["spot", "futures/um", "futures/cm"]),
    default="spot",
    help="choose spot or futures data, default to 'spot'",
)
@click.option(
    "--timeframe",
    default="15m",
    type=click.Choice(TIMEFRAMES),
    help="The timeframe of klines, default to '15m', can be omitted if --data-type is not 'klines'",
)
@click.option(
    "--tz",
    default=None,
    help="The tz database name of time zone, use your local time zone if omitted'",
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
        start=unify_datetime(start),
        end=unify_datetime(end),
        tz_database_name=tz,
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
