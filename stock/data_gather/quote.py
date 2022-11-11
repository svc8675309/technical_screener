import pandas as pd

from datetime import date
from stock.data_gather.statement_utils import StatementUtils
from stock.util.math_utils import MathUtils


class Quote(object):

    """
    Price per Earnings
    """

    __ticker: str = None
    __cur_date: date = None
    __quote: pd.DataFrame
 
    def __init__(self, ticker: str, cur_date: date, data_dir: str = "./data"):
        self.__ticker = ticker
        self.__cur_date = cur_date
        self.__quote = StatementUtils.getStatement(ticker, data_dir, cur_date, "q", True)
 
    def get_price_per_earnings(self) -> int:
        if self.__quote is None:
            return 0

        pe = self.__quote.loc["PE Ratio (TTM)"][0]
        if pe is None or pe < 5 or pe > 50:
            return 0
        else:
            return 1
