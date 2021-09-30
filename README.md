## About The Project
Backtesting made easy: <strong>EVERYONE</strong> can backtest his strategy
## Getting Started
Installation
------------

    $ pip install tradeit
    
Usage
------------

```python
from tradeit.backtester import BacktestWrapper
from tradeit.strategies import Bouncing
from tradeit.optimization import Analyzer, Dataset, DatasetBuilder, ML

# BACKTESTING 
btw = BacktestWrapper(strategy=Bouncing, analysis_type="MIRCRO", log_folder="/tmp/logs")
btr = btw.run(path_to_ur_stocks)

# logs results 
btw.log_results(log_folder)

# ANALYSIS 
analyzer = Analyzer(btr)
analyzer.win_rate()
analyzer.stats()
analyzer.ruin_probability()

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
