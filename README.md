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
from pytrader.analysis import Analyzer

btw = BacktestWrapper(strategy=Bouncing, analysis_type="MIRCRO")
btr = btw.run(path_to_ur_stock)
analyzer = Analyzer(btr)
analyzer.win_rate()
analyzer.stats()
analyzer.ruin_probability()
```
