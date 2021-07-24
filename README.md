


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/abdel-ely-ds/trading-pytradere">
    <img src="logo.png" alt="Logo" width="300" height="150">
  </a>

  <h3 align="center">Backtest Framework for developpers and non developpers</h3>

  <p align="center">
    Backtesting trading strategies made easy
    <br />
    <br />
    ·
    <a href="https://github.com/abdel-ely-ds/trading-pytrader/issues">Report Bug</a>
    ·
    <a href="https://github.com/abdel-ely-ds/trading-pytrader/issues">Request Feature</a>
  </p>
</p>

### Installation

```
pip install pytrader
   ```



<!-- USAGE EXAMPLES -->
## Usage

```python
from pytrader.backtesting import Backtest, Strategy
from pytrader.backtester import crossover

from pytrader.backtester import SMA, GOOG


class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()


bt = Backtest(GOOG, SmaCross, commission=.002,
              exclusive_orders=True)
stats = bt.run()
bt.plot()

   ```

<!-- CONTRIBUTING -->
## Contributing

Feel Free to contribute to the project

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Email - abdel.ely.ds@gmail.com

