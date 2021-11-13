## About The Project
Backtesting made easy: <strong>EVERYONE</strong> can backtest his strategy
## Getting Started
Installation
------------

    $ pip install t_nachine
    
Usage
------------

```python
from t_nachine.backtester import Backtest
from t_nachine.strategies import Bouncing
from t_nachine.optimization import Analyzer, Dataset, DatasetBuilder, ML

# BACKTESTING 
bt = Backtest(cash=10_000)
btr = bt.run(strategy=Bouncing, stock_path=path_to_ur_stocks)

# logs results 
bt.log_results(backtest_results=btr, backtest_name="bounce")

# ANALYSIS 
analyzer = Analyzer(btr)
analyzer.win_rate
analyzer.stats
analyzer.ruin_probability()
analyzer.losing_streak_probability()
analyzer.winning_streak_probability()
analyzer.plot_equity_curve()
analyzer.plot_simulated_equity_curve()

# OPTIMIZATION
indicators = {}
dataset_builder = DatasetBuilder(btr, path_to_ur_stocks, indicators)
dataset: Dataset = dataset_builder.build()

# optimizing 
ml = ML(dataset)
ml.fit()
ml.evaluate()
ml.save()
```
