import pandas as pd
from datetime import datetime
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
 
    @staticmethod
    def apply(stocks: pd.DataFrame):
          stocks["pe"] = stocks.apply(
            lambda row: Quote.apply_row(row), axis=1
        )
    @staticmethod
    def apply_row(row: pd.Series) -> float:
        dr = 0
        ticker_val = row["ticker"]
        date_val = row["date"]
 
        try:
            dt = datetime.strptime(date_val, "%Y-%m-%d").date()
            q = Quote(ticker_val, dt);
            dr = q.get_price_per_earnings()
        except Exception as e:
            dr = 0
            print(f"Quote unable to parse {ticker_val} {date_val}  error = {e}")
        return dr
 
    def get_price_per_earnings(self) -> int:
        if self.__quote is None:
            return 0

        pe = self.__quote.loc["PE Ratio (TTM)"][0]
        if pe is None or pe < 5 or pe > 50:
            return 0
        else:
            return 1
