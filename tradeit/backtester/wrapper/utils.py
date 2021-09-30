import os
import platform

import pandas as pd

from tradeit.constants import *


def post_process_stats(stats: pd.Series, symbol: str) -> pd.DataFrame:
    stats_copy = stats.copy()
    try:
        stats_copy[DURATION] = stats_copy[DURATION].dt.days
        stats_copy[ENTRY_TIME] = pd.to_datetime(stats_copy[ENTRY_TIME])
        stats_copy[EXIT_TIME] = pd.to_datetime(stats_copy[EXIT_TIME])
        stats_copy = stats_copy.to_frame().T
    except (KeyError, AttributeError) as e:
        pass

    stats_copy[SYMBOL] = [symbol] * len(stats_copy)
    return stats_copy


def pre_process_stock(stock: pd.DataFrame) -> pd.DataFrame:
    stock_copy = stock.copy()
    stock_copy.Date = pd.to_datetime(stock.Date)
    stock_copy.set_index(DATE, inplace=True)
    return stock_copy


def pre_process_path(stock_path: str) -> tuple[str, list[str]]:
    try:
        prefix_path = stock_path
        stock_names = os.listdir(stock_path)

    except NotADirectoryError:
        sep = "\\" if platform.system() == "Windows" else "/"
        stocks_path_split = stock_path.split(sep)
        prefix_path = sep.join(stocks_path_split[:-1])
        stock_names = [stocks_path_split[-1]]

    return prefix_path, stock_names


def set_log_folder(log_folder: str) -> str:
    output_dir = os.path.abspath(os.path.expanduser(log_folder))
    if not os.path.exists(output_dir):
        os.mkdir(os.path.abspath(os.path.expanduser(log_folder)))
    return output_dir
