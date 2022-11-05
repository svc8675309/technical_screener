black --line-length 120 ta_yahoo_fin.py

*** TA-LIB
# https://stackoverflow.com/questions/24391964/how-can-i-get-python-h-into-my-python-virtualenv-on-mac-osx
# find /usr/local/Cellar/ -name Python.h
export C_INCLUDE_PATH="/usr/local/Cellar//python@3.9/3.9.15/Frameworks/Python.framework/Versions/3.9/include/python3.9/"

$ python3 -m pip install TA-Lib

pip install talib-binary

# GIT REPO TA-LIB
https://github.com/mrjbq7/ta-lib
***



Candlestick patterns
https://mrjbq7.github.io/ta-lib/funcs.html'

Ta-Lib usage
https://towardsdatascience.com/technical-analysis-of-stocks-using-ta-lib-305614165051
df[['Close','MA']].plot(figsize=(12,12))

https://towardsdatascience.com/trading-strategy-technical-analysis-with-python-ta-lib-3ce9d6ce5614


RSI
https://mrjbq7.github.io/ta-lib/func_groups/momentum_indicators.html
https://www.youtube.com/watch?v=0XQjgmChtE4

Algorithmically Detecting (and Trading) Technical Chart Patterns with Python
https://medium.com/automation-generation/algorithmically-detecting-and-trading-technical-chart-patterns-with-python-c577b3a396ed

Just indicators = 13.8% / 237d
Balance Sheet   = 16.2% / 244d