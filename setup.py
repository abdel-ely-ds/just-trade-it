from setuptools import setup

TEST_DEPS = ["pytest==5.0.1", "pytest-runner==5.1", "pytest-cov==2.7.1", "nox"]

setup(
    name="t_nachine",
    author="Abdellah EL YOUNSI",
    author_email="abdel.ely.ds@gmail.com",
    url="https://github.com/abdel-ely-ds/trading-pytrader",
    keywords="core",
    license="MIT",
    description="backtest strategies",
    long_description="file: README.md",
    classifiers=["Programming Language :: Python :: 3.7"],
    zip_safe=True,
    include_package_data=True,
    version="1.0.0",
    packages=["t_nachine"],
    install_requires=["numpy",
                      "pandas >= 0.25.0, != 0.25.0",
                      "bokeh >= 1.4.0", "tqdm >=4.62.2",
                      "matplotlib",
                      "scipy",
                      "lightgbm",
                      "joblib"],

    tests_require=TEST_DEPS,
    extras_require={"test": TEST_DEPS},
)
