from flask import Flask, render_template, request
import sys
from datetime import date, datetime
import pandas as pd
from stock.data_gather.stock_data import StockData
from stock.util.ta_ai import TaAi
from stock.data_gather.balance_income import BalanceIncome
from stock.data_gather.quote import Quote

app = Flask(__name__)
# FLASK_APP=app.py FLASK_ENV=development flask run --no-debugger
# export FLASK_DEBUG=1
# export FLASK_APP=app.py
# flask run
# flask run --no-debugger
# Get the latests stocks


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        date_var = request.form["date_var"]
        stock_picks: str = request.form["stock_picks"]
        obj_chk = request.form.get("ignore_update")

        ignore_update = False
        if obj_chk is not None:
            ignore_update = True

        end_date = datetime.strptime(date_var, "%Y-%m-%d")
        resource_dir: str = "./data/resource"

        # ( 1 )
        tickers = []
        if len(stock_picks) == 0 or stock_picks == "*":
            
            with open(f"{resource_dir}/nasdaq.csv") as f:
                tickers = f.read().splitlines()
        else:
            stock_picks = stock_picks.strip()
            for item in stock_picks.split(","):
                item = item.strip()
                tickers.append(item)

        # ( 2 - create new data frames constrained by date )
        stocks: dict = StockData.get_stocks_by_dates(
            tickers, 5, end_date
        )

        # Get candlestick data
        candlesticks = {}            
        with open(f"{resource_dir}/ta_candlesticks.csv") as f:
            items = f.read().splitlines()
            for item in items:
                candlesticks[item.split(",")[0]] = item.split(",")[1]
        candlesticks = candlesticks.items()        

        # Scan for technical indicators
        cans_df: pd.DataFrame = TaAi().scan(
            candlesticks, stocks, f"{resource_dir}/candlesticks_2021-06-24_18675.csv",
        )

        print(cans_df)
        cans_df = cans_df.loc[cans_df["condition"] == "bullish"].copy()
        cans_df = cans_df.loc[cans_df["close"] > 2 ]
        cans_df = cans_df.sort_values(["correctness"], ascending=[False])
        cans_df = cans_df.head(100)
        
        if len(tickers) > 10:
            # Financials
            BalanceIncome.apply(cans_df)
            cans_df["finance"] = pd.to_numeric(
                cans_df["correctness"]
            ) + pd.to_numeric(cans_df["roe"])
            cans_df = cans_df.sort_values(["finance"], ascending=[False])
            Quote.apply(cans_df)
            cans_df = cans_df.loc[cans_df["pe"] == 1]

        # pd.set_option("display.max_rows", None, "display.max_columns", None)
        pd.set_option("display.max_rows", None)
        print(cans_df, file=sys.stdout)

        cans_df = cans_df.head(20)
        return render_template(
            "index.html",
            stocks=cans_df.to_dict(orient="index"),
            date_var=date_var,
            stock_picks=stock_picks,
            ignore_update=obj_chk,
        )
    else:
        return render_template(
            "index.html",
            stocks={},
            date_var=date.today().strftime("%Y-%m-%d"),
            stock_picks="*",
            ignore_update=None,
        )

