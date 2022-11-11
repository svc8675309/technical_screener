from pprint import pprint
from time import strptime
from flask import Flask, render_template, request
import sys
from datetime import date, datetime
from yh_utils import YhUtils
from ta_ai import TaAi
import pandas as pd
from yh_balance_sheet import YhBalanceSheet
from yh_income_statement import YhIncomeStatement
from yh_cash_flows import YhCashFlows
from yh_balance_income import YhBalanceIncome
from yh_summary import YhSummary

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

        # ( 1 )
        # tickers_lookup = YhUtils.csv_to_dict(["./resources/companies.csv"])
        tickers_lookup = YhUtils.csv_to_dict(
            [
                "./resources/nasdaqlisted.csv",
                "./resources/companies.csv",
                "./resources/nasdaq.csv",
            ]
        )
        tickers = []
        if len(stock_picks) == 0 or stock_picks == "*":
            # ( 2 )
            # tickers = YhUtils.csv_to_tuple(["./resources/companies.csv"])
            tickers = YhUtils.csv_to_tuple(
                [
                    "./resources/nasdaqlisted.csv",
                    "./resources/companies.csv",
                    "./resources/nasdaq.csv",
                ]
            )
        else:
            stock_picks = stock_picks.strip()
            for item in stock_picks.split(","):
                item = item.strip()
                tickers.append((item, tickers_lookup[item][0]))

        # ( 3 )
        candidates: dict = YhUtils.get_stocks_by_dates(
            tickers, 5, end_date, ignore_update
        )

        candlesticks = YhUtils.csv_to_tuple(["./resources/ta_candlesticks.csv"])
        candidates = TaAi(verbose=True).scan(
            candlesticks, candidates, "./analysis/candlesticks_2021-06-24_18675.csv",
        )

        if len(tickers) > 10:
            # Financials
            #YhIncomeStatement.apply(candidates)
            YhBalanceSheet.apply(candidates)
            candidates["Finance"] = pd.to_numeric(
                candidates["Correctness"]
            ) + pd.to_numeric(candidates["balance_s"])
            candidates = candidates.sort_values(["Finance"], ascending=[False])
            candidates = candidates.loc[candidates["Condition"] == "bullish"].copy()
            YhSummary.apply(candidates)
            candidates = candidates.loc[candidates["pe"] == 1]

        # pd.set_option("display.max_rows", None, "display.max_columns", None)
        pd.set_option("display.max_rows", None)
        print(candidates, file=sys.stdout)

        #candidates = candidates.head(20)
        return render_template(
            "index.html",
            stocks=candidates.to_dict(orient="index"),
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

