## About The Project
Backtesting made easy: <strong>EVERYONE</strong> can backtest his strategy
## Getting Started
Installation
------------

    $ pip install pytrader
    
Usage
------------

```python
from pytrader.backtester import BacktestWrapper
from pytrader.strategies import Bouncing
from pytrader.optimization import Analyzer

# run 
btw = BacktestWrapper(strategy=Bouncing, analysis_type="MIRCRO", log_folder="/tmp/logs")
btr = btw.run(path_to_ur_stock)

# logs results 
btw.log_results(log_folder)

# optimization 
analyzer = Analyzer(btr)
analyzer.win_rate()
analyzer.stats()
analyzer.ruin_probability()
```
