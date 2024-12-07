import pandas as pd
from datetime import datetime
from datetime import date
from stock.data_gather.statement_utils import StatementUtils
from stock.util.math_utils import MathUtils
from typing import List


class BalanceIncome(object):

    """
    Both the balance sheet and income
    Return on Equity

    """

    __ticker: str = None
    __cur_date: date = None
    __balance_sheet: pd.DataFrame
    __income_statement: pd.DataFrame

    def __init__(self, ticker: str, cur_date: date, data_dir: str = "./data"):
        self.__ticker = ticker
        self.__cur_date = cur_date
        self.__balance_sheet = StatementUtils.getStatement(ticker, data_dir, cur_date, "b", False)
        self.__income_statement = StatementUtils.getStatement(ticker, data_dir, cur_date, "i", False)

    @staticmethod
    def get_data(tickers: List[str]):
        date_val = date.today()
        for ticker in tickers:
            try:
                BalanceIncome(ticker, date_val)
            except Exception as e:
                print(f"BalanceIncome({ticker},{date_val}) failed. Error: {e}")    

    @staticmethod
    def apply(stocks: pd.DataFrame):
        stocks["roe"] = stocks.apply(lambda row: BalanceIncome.apply_row(row), axis=1)

    @staticmethod
    def apply_row(row: pd.Series) -> float:
        dr = 0
        ticker_val = row["ticker"]
        date_val = row["date"]

        try:
            dt = datetime.strptime(date_val, "%Y-%m-%d").date()
            bi = BalanceIncome(ticker_val, dt)
            dr = bi.get_return_on_equity()
        except Exception as e:
            dr = 0
            print(f"BalanceIncome unable to parse {ticker_val} {date_val} error = {e}")
        return dr

    def get_return_on_equity(self) -> int:
        """_summary_ examines a trend in netIncome over totalStockholderEquity ( Return on Equity )
        Return on equity (ROE) is a measure of financial performance calculated by dividing net income by shareholders' equity.
        Because shareholders' equity is equal to a company's assets minus its debt, ROE is considered the return on net assets.

        The higher the ROE, the better a company is at converting its equity financing into profits.
        if a company has ROE above 20%, it is considered a good investment.

        All we care about here is the slope, meaning is a companies ROE imporving?

        Returns:
            int: _description_ if ROE is postive or negative between 1 and -1
        """
        # make sure the dates are the same
        try:
            net_incomes = self.__income_statement.loc["netIncome"].values.tolist()
            total_equities = self.__balance_sheet.loc["totalStockholderEquity"].values.tolist()
            if len(net_incomes) != len(total_equities):
                print(f"Balance sheet and income data do not match for stock {self.__ticker}")
                return 0
            else:
                # Return on Equity Array
                index = 0
                roe_array = []
                for te in total_equities:
                    ni = net_incomes[index]
                    if ni != 0 and te != 0:
                        roe_array.append(ni / te)
                    index = index + 1
                return_on_equity_slope = MathUtils.best_fit_slope(roe_array) * 100
                # can't tell
                if return_on_equity_slope == 0:
                    return 0

                # 1 is a 45 deg angle or 100%
                # .2 for 20%
                if return_on_equity_slope >= 0.2:
                    return 2
                else:
                    return -1

        except Exception as e:
            print(f"BalanceIncome.get_return_on_equity() Exception for stock {self.__ticker}: Error {e}")
            return 0
