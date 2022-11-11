from yh_financials import YhFinancials
import pandas as pd
import numpy as np
from yh_utils import YhUtils

class YhCashFlows(object):
    """
    Report of cash collected and cash paid during a period of time.
    ( report of cash in and out )
    where did the money come from
    where did the money go

    Operating activities
        does every day
    investing activities
        investing in the business ( occasionally )
        Cap X - Capitol expenditure 
        Free Cash Flow
            spend any way
            finance flexibility
    financing activities
        cash comes in
        cash out dividends  / loans

    totalCashFromOperatingActivities  + making money - loosing    
    """

    __ticker: str = None
    __sDate: str = None
    financials: pd.DataFrame = None

    def __init__(self, ticker: str, sDate: str, data_dir: str = "./data"):
        self.__ticker = ticker
        self.__sDate = sDate
        t_dir = data_dir + "/cash_flow"
        dicts: dict = YhFinancials.get_financials([(ticker, "")], t_dir)
        self.financials = dicts.get(ticker)

    @staticmethod
    def apply(stocks: pd.DataFrame):
        stocks["op_ac"] = stocks.apply(
            lambda row: YhCashFlows.cash_flow_indicators(row), axis=1
        )

    @staticmethod
    def cash_flow_indicators(row: pd.Series) -> float:
        oa = YhCashFlows(row["Ticker"], row["Date"]).get_operating_activities()
        return oa

    def get_operating_activities(self) -> int:
        try:
            if self.financials is None or len(self.financials) == 0:
                return 0

            oa = self.financials["totalCashFromOperatingActivities"].tolist()
            # Calculate the best fit slope
            oa_slope = YhUtils.best_fit_slope(oa)
            # can't tell
            if oa_slope == 0:
                return 0

            oa_mean = np.mean(oa)

            if oa_mean > 0:
                if oa_slope > 1:
                    return 2
                else:
                    return 1
            else:
                if oa_slope > 1:
                    return -1
                else:
                    return -2
        except Exception as e:
            print(
                f"YhCashFlows.get_operating_activities() Exception for stock {self.__ticker}: Error {e}"
            )
            return 0            
