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
    def get_data(tickers: List[str], data_dir: str = "./data/ticker", look_back_days: int = 1800) -> dict:
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
                    # Need to account for saturday and sunday
                    weekend = 0
                    if wd == 5:
                        weekend = 1
                    elif wd == 6:
                        weekend = 2

                    # get the date of the last row
                    latest_in_df = df.iloc[-1][0]
                    # increase the last recorded day by 1 day
                    latest_date = datetime.strptime(latest_in_df, "%Y-%m-%d")

                    # if the last date was friday and today is sat then firday !< sat - 1
                    if latest_date.date() < (end_date - timedelta(days=weekend)):
                        try:
                            # We must add 1 day to the last_date for the query so not to include the last_date
                            adjusted = si.get_data(ticker, start_date=latest_date.date() + timedelta(days=1))
                        except Exception as ex:
                            print(f"Yahoo_fin :Error downloading : {ticker} : {str(ex)}")
                            continue
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
                            temp = temp.drop_duplicates(subset=["date"], keep="last")
                            # append to the existing file
                            with open(f"{data_dir}/{ticker}.csv", "a") as f:
                                temp.to_csv(f, header=False, index=False)

                            # reload ( this solves the index problem )
                            df: pd.DataFrame = pd.read_csv(f"{data_dir}/{ticker}.csv")
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

    @staticmethod
    def get_stocks_by_dates(
        tickers: List[str],
        look_back: int,
        end_date: date,
        data_dir: str = "./data/ticker",
    ) -> dict:
        """Looks in the data dir for a ticker and returns a data frame with start and end dates
        that correspond with end_date + lookback

        Args:
            tickers (List[str]): _description_
            look_back (int): _description_
            end_date (date): _description_
            data_dir (str, optional): _description_. Defaults to "./data/ticker".

        Returns:
            dict: _description_
        """

        # Can't be a weekend day
        wd = end_date.weekday() - 4
        if wd > 0:
            end_date = end_date - timedelta(wd)

        # At least a week
        start = (int(look_back / 7) + 1) * 7

        start_date = end_date - timedelta(start)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        ret_dict = {}
        for ticker in tickers:
            try:
                df: pd.DataFrame = pd.read_csv(f"{data_dir}/{ticker}.csv")
                df: df.set_index("Date")[start_date_str:end_date_str].tail(look_back)
                ret_dict[ticker] = df
            except Exception as e:
                print(f"Error getting dates {start_date_str}:{end_date_str} lookback {look_back} for ticker={ticker}")
        return ret_dict


# two_d_array = StockData.group_by_char(si.tickers_nasdaq())
# print(two_d_array)

# StockData.get_data(si.tickers_nasdaq())

# StockData.get_data(["AACG"])
