import pandas as pd
from typing import List
import os
from calendar import monthrange
from datetime import date
from datetime import timedelta
from datetime import datetime
from yahoo_fin import stock_info as si

# open,high,low,close,adjclose,volume,ticker
class StockData(object):
    @staticmethod
    def get_data(
        tickers: List[str], data_dir: str = "./data/ticker", look_back_days: int = 1800
    ) -> dict:
        if tickers is None:
            return None

        end_date = date.today()
        start_date = end_date - timedelta(days=look_back_days)

        # Create a dir with the date that we polled the data
        if not os.path.exists(data_dir):
            # need to pull data
            os.makedirs(data_dir)

        # Cache all stock symbol by dataframes
        ret_dict = {}
        count = 0
        for ticker in tickers:
            count = count + 1
            print(f"{count}/{len(tickers)}", end="\r")
            if not os.path.exists(f"{data_dir}/{ticker}.csv"):
                print(f"Downloading New : {ticker}")
                try:
                    df = si.get_data(ticker, start_date=start_date, end_date=end_date)
                    df.index.names = ["date"]
                    df.to_csv(f"{data_dir}/{ticker}.csv")
                    ret_dict[ticker] = df
                except Exception as e:
                    print(f"Failed downloading : {ticker} : {str(e)}")
            else:
                df: pd.DataFrame = pd.read_csv(f"{data_dir}/{ticker}.csv")
                if len(df) > 0:
                    wd = end_date.weekday()
                    # If it's not sunday or monday
                    if wd != 6 and wd != 0:
                        # get the date of the last row
                        latest_in_df = df.iloc[-1][0]
                        # increase the last recorded day by 1 day
                        latest_date = datetime.strptime(
                            latest_in_df, "%Y-%m-%d"
                        ) + timedelta(days=1)
                        if latest_date.date() < end_date:
                            adjusted = si.get_data(
                                ticker, start_date=latest_date.date(), end_date=end_date
                            )
                            if len(adjusted) > 0:
                                temp: pd.DataFrame = pd.DataFrame(
                                    columns=(
                                        "date",
                                        "open",
                                        "high",
                                        "low",
                                        "close",
                                        "adjclose",
                                        "volume",
                                    )
                                )
                                for index, row in adjusted.iterrows():
                                    r_date = index.strftime("%Y-%m-%d")
                                    r_list = row.to_list()
                                    temp.loc[temp.shape[0]] = [
                                        r_date,
                                        r_list[0],
                                        r_list[1],
                                        r_list[2],
                                        r_list[3],
                                        r_list[4],
                                        r_list[5],
                                    ]
                                temp = temp.drop_duplicates(
                                    subset=["date"], keep="last"
                                )
                                # append to the existing file
                                with open(f"{data_dir}/{ticker}.csv", "a") as f:
                                    temp.to_csv(f, header=False, index=False)

                                # reload ( this solves the index problem )
                                df: pd.DataFrame = pd.read_csv(
                                    f"{data_dir}/{ticker}.csv"
                                )
                                print(f"Updated {ticker}\n")
                    ret_dict[ticker] = df
        return ret_dict

    @staticmethod
    def group_by_char(tickers: List) -> List[List[str]]:
        # sort them
        util_func = lambda x, y: x[0] == y[0]
        res = []
        for ticker in tickers:
            ele = next((x for x in res if util_func(ticker, x[0])), [])
            if ele == []:
                res.append(ele)
            ele.append(ticker)
        return res


# two_d_array = StockData.group_by_char(si.tickers_nasdaq())
# print(two_d_array)

# StockData.get_data(si.tickers_nasdaq())

# StockData.get_data(["AACG"])
