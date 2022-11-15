from typing import List
import pandas as pd
from typing import Tuple

from pandas.core.frame import DataFrame
import talib


class TaAi(object):

    # ------------------------------- Candlestick Daily scan ( 5 day period )
    def scan(
        self,
        candlesticks: List[Tuple[str, str]],
        stocks: dict,
        cs_analysis_file,
    ) -> pd.DataFrame:
        """
        scan a section of stock data for a candlestick pattern
        """
        cs_analysis: pd.DataFrame = pd.read_csv(cs_analysis_file)
        cs_analysis = cs_analysis.set_index("candlestick")

        results = pd.DataFrame(
            columns=(
                "date",
                "candlestick",
                "condition",
                "ticker",
                "correctness",
                "slope",
                "window",
                "name",
                "description",
            )
        )
        count = 0
        for candlestick, desc in candlesticks:
            count = count + 1
            print(f"candlestick scan : {count}/{len(candlesticks)}", end="\r")
            for ticker, stock_data in stocks.items():
                if stock_data.shape[0] > 0:
                    # Run talib to see if there are any matches
                    pattern_function = getattr(talib, candlestick)
                    # tuple list to Df
                    hits: pd.Series = pattern_function(
                        stock_data["open"],
                        stock_data["high"],
                        stock_data["low"],
                        stock_data["close"],
                    )

                    # keep only the hits
                    hits = hits[hits != 0].dropna()
                    if hits.empty:
                        continue
                    hit = hits.tail(1)
                    # is this the last hit
                    if stock_data.index.values[-1] == hit.index[0]:
                        val = hit.values[0]

                        if val < 0:
                            condition = "bearish"
                            candlestick_t = candlestick + "_BEAR"
                        else:
                            condition = "bullish"
                            candlestick_t = candlestick + "_BULL"

                        cs_analysis_filtered: DataFrame = cs_analysis.loc[
                            cs_analysis.index.values == candlestick_t
                        ]
                        if len(cs_analysis_filtered) == 0:
                            print(
                                f"{candlestick_t} does not exist in {cs_analysis_file}"
                            )
                            continue

                        corretness = (
                            str(int(cs_analysis_filtered.iloc[0]["correctness"] * 100))
                        )
                        slope = cs_analysis_filtered.iloc[0]["slope"]
                        window = str(cs_analysis_filtered.iloc[0]["window"]) + "d"

                        dstr = hit.index[0]
                        if str(dstr).isnumeric():
                            dstr = stock_data.tail(1)["date"].values[0]
                        results.loc[len(results)] = [
                            dstr,
                            candlestick,
                            condition,
                            ticker,
                            corretness,
                            slope,
                            window,
                            ticker,
                            desc,
                        ]
        results = results.sort_values("correctness", ascending=False)
        results = results.reset_index(drop=True)
        return results

