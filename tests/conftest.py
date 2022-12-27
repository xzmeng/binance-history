from binance_history import config
import pytest


@pytest.fixture(scope="session", autouse=True)
def set_cache_dir(tmp_path_factory):
    config.CACHE_DIR = tmp_path_factory.getbasetemp()
