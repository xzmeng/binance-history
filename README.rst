===============
Binance History
===============

.. image:: https://img.shields.io/pypi/v/binance-history
    :target: https://pypi.org/project/binance-history/
    :alt: pypi version

.. image:: https://img.shields.io/github/license/xzmeng/binance-history
    :target: https://github.com/xzmeng/binance-history/blob/master/LICENSE
    :alt: License - MIT

.. image:: https://img.shields.io/codecov/c/github/xzmeng/binance-history
    :target: https://codecov.io/github/xzmeng/binance-history
    :alt: Coverage

.. image:: https://img.shields.io/github/actions/workflow/status/xzmeng/binance-history/tests.yml?label=tests
    :target: https://github.com/xzmeng/binance-history/actions
    :alt: Tests Status

.. image:: https://readthedocs.org/projects/binance-history/badge/?version=latest
    :target: https://binance-history.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/binance-history
   :alt: PyPI - Python Version

Fetch binance public data easily.

Supports Python **3.8+**.

Installation
============

.. code-block:: bash

    $ pip install binance-history

Usage
=====
`API docs <https://binance-history.readthedocs.io>`_

Klines
------

.. code-block:: python

    >>> import binance_history as bh
    >>> klines = bh.fetch_klines(
    ...     symbol="BTCUSDT",
    ...     timeframe="1m",
    ...     start="2022-12-14",
    ...     end="2022-12-24",
    ... )
                                   open      high       low     close     volume  quote_volume  trades                   close_datetime
    open_datetime
    2022-12-14 00:00:00+08:00  17753.54  17768.41  17752.78  17766.99  240.82918  4.277685e+06    5241 2022-12-14 00:00:59.999000+08:00
    2022-12-14 00:01:00+08:00  17766.99  17786.40  17764.37  17781.81  311.47670  5.536668e+06    6278 2022-12-14 00:01:59.999000+08:00
    2022-12-14 00:02:00+08:00  17781.81  17790.54  17771.44  17785.37  372.12992  6.616562e+06    6911 2022-12-14 00:02:59.999000+08:00
    2022-12-14 00:03:00+08:00  17786.23  17800.18  17774.63  17777.35  401.52223  7.142210e+06    6926 2022-12-14 00:03:59.999000+08:00
    2022-12-14 00:04:00+08:00  17777.35  17785.98  17769.15  17781.93  218.03837  3.876373e+06    5519 2022-12-14 00:04:59.999000+08:00
    ...                             ...       ...       ...       ...        ...           ...     ...                              ...
    2022-12-23 23:56:00+08:00  16850.22  16850.22  16839.55  16842.59  146.38906  2.465894e+06    4229 2022-12-23 23:56:59.999000+08:00
    2022-12-23 23:57:00+08:00  16842.59  16846.22  16839.00  16840.99   86.95440  1.464495e+06    3152 2022-12-23 23:57:59.999000+08:00
    2022-12-23 23:58:00+08:00  16840.99  16843.61  16827.28  16830.27  208.41471  3.508642e+06    4918 2022-12-23 23:58:59.999000+08:00
    2022-12-23 23:59:00+08:00  16830.27  16836.66  16824.41  16832.16  154.10833  2.593717e+06    4502 2022-12-23 23:59:59.999000+08:00
    2022-12-24 00:00:00+08:00  16832.15  16833.62  16828.42  16830.52  119.28572  2.007721e+06    3725 2022-12-24 00:00:59.999000+08:00

    [14401 rows x 8 columns]

AggTrades
---------

.. code-block:: python

    >>> bh.fetch_agg_trades(
    ...     symbol="ETCBTC",
    ...     start="2022-11 01:05",
    ...     end="2022-11-25 3:20",
    ...     tz="Europe/Paris"
    ... )
                                        price  quantity  is_buyer_maker
    datetime
    2022-11-01 01:05:09.435000+01:00  0.001187      1.60            True
    2022-11-01 01:05:17.639000+01:00  0.001186     29.56            True
    2022-11-01 01:05:18.616000+01:00  0.001186      8.43            True
    2022-11-01 01:05:18.621000+01:00  0.001186     37.31            True
    2022-11-01 01:05:18.748000+01:00  0.001186      0.17            True
    ...                                    ...       ...             ...
    2022-11-25 03:19:18.317000+01:00  0.001199      5.00           False
    2022-11-25 03:19:19.482000+01:00  0.001199     10.69           False
    2022-11-25 03:19:23.270000+01:00  0.001199      7.55            True
    2022-11-25 03:19:26.082000+01:00  0.001199      2.56            True
    2022-11-25 03:19:40.375000+01:00  0.001199      2.20           False


Command Line
------------
**binance-history** comes with a command line interface,
you need to install some extra dependencies to use it:

.. code-block:: bash

    $ pip install 'binance-history[cli]'


.. code-block:: bash

    $ bh --help
    Usage: bh [OPTIONS]

    Options:
      --symbol TEXT                   The binance market pair name, e.g. BTCUSDT
                                      [required]
      --start TEXT                    The start datetime, e.g. '2022-1-2 1:10'
                                      [required]
      --end TEXT                      The end datetime, e.g. '2022-1-25 2:20
                                      [required]
      --data-type [klines|aggTrades]  choose klines or aggTrades to download,
                                      default to 'klines'
      --asset-type [spot|futures/um|futures/cm]
                                      choose spot or futures data, default to
                                      'spot'
      --timeframe [1s|1m|3m|5m|15m|30m|1h|2h|4h|6h|8h|12h|1d|3d|1w|1M]
                                      The timeframe of klines, default to '15m',
                                      can be omitted if --data-type is not
                                      'klines'
      --tz TEXT                       The tz database name of time zone, use your
                                      local time zone if omitted'
      --output-path TEXT              The path you want to save the downloaded
                                      data, support format: [csv, json, xlsx],
                                      e.g. a.xlsx  [required]
      --help                          Show this message and exit.

    $ bh --start 2022-1-5 --end 2022-1-7 --symbol ETCBTC --output-path a.xlsx
