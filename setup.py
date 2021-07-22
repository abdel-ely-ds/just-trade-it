from setuptools import setup

setup(
    name='pytrader',
    version='1.0.0',

    packages=['src'],
    install_requires=['numpy',
                      'pandas >= 0.25.0, != 0.25.0',
                      'bokeh >= 1.4.0'],

    url='https://github.com/abdel-ely-ds/trading-pytrader',
    python_requires='>=3.6',

    author='Abdel ELYDS',
    author_email='abdel.ely.ds@gmail.com',

    license='MIT',

    description='backtest strategies')
