import json

import click
import pandas as pd
from click.termui import prompt
from numpy import promote_types
from pytrader.backtester.backtesting import Backtest, Strategy
from pytrader.backtester.wrapper.exceptions import (
    ALLOWED_ANALYSIS_TYPES,
    AnalysisNotAllowedError,
)
from pytrader.backtester.wrapper.log_handler import LogHandler

from .utils import update_strategy


@click.command(name="pytrader-bt")
@click.option(
    "--strategy",
    required=True,
    type=Strategy,
    help="The strategy to backtest",
    prompt="strategy please",
)
@click.option(
    "--backtest-name",
    type=str,
    required=True,
    help="the name to give to your backtest experiment",
    prompt="backtest name please",
)
@click.option(
    "--stock",
    required=True,
    type=pd.Series,
    help="the stock to backtest",
    prompt="stock please",
)
@click.option(
    "--cash", required=False, default=20_000, type=float, help="intial capital"
)
@click.option("--commision", required=False, default=0.0, type=float, help="commision")
@click.option(
    "--exclusive-orders",
    required=False,
    default=False,
    type=bool,
    help="exclusive or not",
)
@click.option(
    "--strategy-attrs", required=False, default=None, type=dict, help="exclusive or not"
)
@click.option(
    "--analysis-type",
    Required=False,
    default="MACRO",
    type=str,
    help="which analysis to conduct there are two types: MARCO, MICRO ",
)
@click.option(
    "--log-handler",
    Required=False,
    default=LogHandler(),
    type=LogHandler,
    help="log handler",
)
def execute(
    strategy: Strategy,
    backtest_name: str,
    stock: pd.Series,
    cash: int = 20_000,
    commission: int = 0.0,
    exclusive_orders: bool = False,
    strategy_attrs: dict = None,
    analysis_type: str = "MACRO",
    log_handler: LogHandler = LogHandler(),
) -> json:
    # checks
    if analysis_type not in ALLOWED_ANALYSIS_TYPES:
        raise AnalysisNotAllowedError(analysis_type)

    # handling logs
    backtest_name = log_handler.handle_backtest_name(backtest_name)

    updated_strategy = update_strategy(strategy, strategy_attrs)
    bt = Backtest(
        stock,
        updated_strategy,
        cash=cash,
        commission=commission,
        exclusive_orders=exclusive_orders,
    )
    stats = bt.run()
    stats = stats[ALLOWED_ANALYSIS_TYPES[analysis_type]]

    # todo: process stats

    return stats.to_json(orient="split")
