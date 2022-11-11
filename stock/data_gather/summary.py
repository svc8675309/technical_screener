from yh_financials import YhFinancials
import pandas as pd
from yh_utils import YhUtils


class YhSummary(object):

    """
    Price per Earnings
    """

    __ticker: str = None
    __sDate: str = None
    summary: dict = None

    def __init__(
        self, ticker: str, sDate: str, force_update=False, data_dir: str = "./data"
    ):
        self.__ticker = ticker
        self.__sDate = sDate
        dicts: dict = YhFinancials.get_summary([(ticker, "")], force_update, data_dir)
        self.summary = dicts.get(ticker)

    @staticmethod
    def apply(stocks: pd.DataFrame, force_update=False):
        stocks["pe"] = stocks.apply(
            lambda row: YhSummary.apply_pe(row, force_update), axis=1
        )

    @staticmethod
    def apply_pe(row: pd.Series, force_update) -> float:
        pe = YhSummary(
            row["Ticker"], row["Date"], force_update
        ).get_price_per_earnings()
        return pe

    def get_price_per_earnings(self) -> int:
        if self.summary is None:
            return 0

        trailingPE = self.summary.get("trailingPE")
        if trailingPE is None or trailingPE < 5 or trailingPE > 50:
            return 0
        else:
            return 1
