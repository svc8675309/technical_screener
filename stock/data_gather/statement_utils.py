from yahoo_fin import stock_info as si
import pandas as pd
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

# http://theautomatic.net/yahoo_fin-documentation/
class StatementUtils(object):
    @staticmethod
    def getStatement(
        ticker: str, data_dir: str, cur_date: date, statement_type: str, current_only=False
    ) -> pd.DataFrame:
        """
        data_dir - ./data
        cur_date - the date of the ticker
        statement_type - c : cash flow
                         b : balance
                         i : income
                         q : quote
        current_only - only return a column for the current date, else all date columns are returnd
                        ( but not future columns if date is in the past)
                       quote only returns data for the current day! No historical data
        """
        valid_s_types = {"c", "b", "i", "q"}
        statement_type = statement_type.lower()
        if not ticker:
            raise ValueError("StatementUtils.getStatement() Error : ticker is required")
        if not data_dir:
            raise ValueError("StatementUtils.getStatement() Error : data_dir is required")
        if not cur_date:
            raise ValueError("StatementUtils.getStatement() Error : cur_date is required")
        if not statement_type:
            raise ValueError("StatementUtils.getStatement() Error : statement_type is required")
        if statement_type not in valid_s_types:
            raise ValueError(f"StatementUtils.getStatement() Error : statement_type {statement_type} is not valid ")

        # we can go back no more than a year so...
        lookback = relativedelta(cur_date, date.today())
        if lookback.days > 365:
            return None

        if statement_type == "c":
            return StatementUtils.__get_statement(ticker, f"{data_dir}/cash", cur_date, False, si.get_cash_flow)
        elif statement_type == "i":
            return StatementUtils.__get_statement(
                ticker, f"{data_dir}/income", cur_date, False, si.get_income_statement
            )
        elif statement_type == "b":
            return StatementUtils.__get_statement(ticker, f"{data_dir}/balance", cur_date, False, si.get_balance_sheet)
        elif statement_type == "q":
            if current_only is False:
                raise ValueError(
                    f"StatementUtils.getStatement() Error : Quote only returns current data. current_only must be True"
                )
            qDict: dict = si.get_quote_table(ticker)
            # quote is always today
            return pd.DataFrame(qDict.items(), columns=["Breakdown", datetime.now().strftime("%Y-%m-%d")]).set_index('Breakdown')
        else:
            raise ValueError(f"StatementUtils.getStatement() Error : statement_type {statement_type} is not valid ")

    @staticmethod
    def __get_statement(ticker: str, data_dir: str, cur_date: date, current_only, func) -> pd.DataFrame:
        file = f"{data_dir}/{ticker}.csv"
        if not os.path.exists(file):
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            df = func(ticker, yearly=False)
            df.to_csv(file)
            df = pd.read_csv(file)
        else:
            # load the file
            df = pd.read_csv(file)
            # corner case... where the statement needs to be updated
            # Get the latest colums date and compare it with today
            last_statement_date = datetime.strptime(df.columns[1], "%Y-%m-%d").date()
            delta = relativedelta(cur_date, last_statement_date)
            if delta.days > 90:
                print(f"Attempting to load a {data_dir} statement for ticker {ticker}")
                df = func(ticker, yearly=False)
                df.to_csv(file)

        # 'Breakdown', '2022-06-30', '2022-03-31', '2021-12-31', '2021-09-30']
        # how far in the past is the date?
        for i in range(1, 4):
            print(f"Looking back {ticker} for {data_dir} statement {df.columns[i]}")

            sd_date = datetime.strptime(df.columns[i], "%Y-%m-%d").date()
            if cur_date > sd_date:
                if current_only:
                    # https://sparkbyexamples.com/pandas/pandas-create-new-dataframe-by-selecting-specific-columns/
                    return df[[df.columns[0], df.columns[i]]].copy()
                else:
                    # user wants more than 1 colum
                    if i == 1:
                        return df.set_index('Breakdown')
                    elif i == 2:
                        return df[[df.columns[0], df.columns[2], df.columns[3], df.columns[4]]].copy().set_index('Breakdown')
                    elif i == 3:
                        return df[[df.columns[0], df.columns[3], df.columns[4]]].copy().set_index('Breakdown')
                    else:
                        return df[[df.columns[0], df.columns[4]]].copy().set_index('Breakdown')
        #  no date possible
        return None


ticker = "AACG"
"""
print("income--------------------------------------------------------")
print(StatementUtils.getStatement(ticker, "./data", date.today(), "i"))
print("cash----------------------------------------------------------")
print(StatementUtils.getStatement(ticker, "./data", date.today(), "c"))
print("balance sheet-------------------------------------------------")
print(StatementUtils.getStatement(ticker, "./data", date.today(), "b"))
print("quote---------------------------------------------------------")
print(StatementUtils.getStatement(ticker, "./data", date.today(), "q", True))
"""

"""
Note: for only 1 current_only = True
Note: fewer than 4 data columns may be returned if the date is in the past and current_only = False

income--------------------------------------------------------
                                    2021-12-31   2020-12-31   2019-12-31   2018-12-31
Breakdown                                                                            
researchDevelopment                 11801545.0    8832488.0   11817255.0   19594484.0
effectOfAccountingCharges                  NaN          NaN          NaN          NaN
incomeBeforeTax                    -37949694.0 -110853584.0 -141261615.0  -68053474.0
minorityInterest                     3130442.0   49341369.0   50391547.0   39576017.0
netIncome                          -33649593.0  -92198032.0 -122253989.0  854925914.0
sellingGeneralAdministrative       159405506.0  153597900.0  116035728.0   49078025.0
grossProfit                        104795550.0   57742215.0   18424840.0   -2912859.0
ebit                               -66389483.0 -104357949.0 -108839996.0  -67791950.0
operatingIncome                    -66389483.0 -104357949.0 -108839996.0  -67791950.0
otherOperatingExpenses                -22018.0    -330224.0    -588147.0   -3793418.0
interestExpense                            NaN          NaN          NaN          NaN
extraordinaryItems                         NaN          NaN          NaN          NaN
nonRecurring                               NaN          NaN          NaN          NaN
otherItems                                 NaN          NaN          NaN          NaN
incomeTaxExpense                    -1539577.0  -10268836.0   -7149119.0          0.0
totalRevenue                       202209465.0  162167547.0   97770167.0    1338592.0
totalOperatingExpenses             268598948.0  266525496.0  206610163.0   69130542.0
costOfRevenue                       97413915.0  104425332.0   79345327.0    4251451.0
totalOtherIncomeExpenseNet          28439789.0   -6495635.0  -32421619.0    -261524.0
discontinuedOperations                     NaN          NaN    4894197.0  918665587.0
netIncomeFromContinuingOps         -36410117.0 -100584748.0 -134112496.0  -68053474.0
netIncomeApplicableToCommonShares  -35932682.0  -98382604.0 -128262480.0  835591366.0

cash----------------------------------------------------------
                     2022-06-30  2022-03-31  2021-12-31  2021-09-30
Breakdown                                                          
netIncome             -22070027   -15853876    -2549997   -26200973
changeToLiabilities           0           0           0           0

balance sheet-------------------------------------------------
                               2022-06-30   2022-03-31   2021-12-31   2021-09-30
Breakdown                                                                       
intangibleAssets               84856111.0   89224444.0   93352778.0   97661111.0
capitalSurplus                540765380.0  540576988.0  540583564.0  540513460.0
totalLiab                     329032839.0  319148853.0  316275776.0  329919315.0
totalStockholderEquity        150899153.0  172112190.0  187769092.0  190153331.0
minorityInterest                2427561.0    2553060.0    3130442.0    3977918.0
otherCurrentLiab              227056775.0  208692644.0  225871813.0  223142487.0
totalAssets                   482359553.0  493814103.0  507175310.0  524050564.0
commonStock                     4720147.0    4720147.0    4720147.0    4720147.0
retainedEarnings             -348079921.0 -326009894.0 -310156018.0 -307606020.0
otherLiab                      18696687.0   22767992.0   24931322.0   21171739.0
goodWill                      194754963.0  194754963.0  194754963.0  194754963.0
treasuryStock                 -46506453.0  -47175051.0  -47378601.0  -47474256.0
otherAssets                    25407110.0   26085747.0   26739026.0   28702127.0
cash                           60516273.0   62413833.0   71339361.0   75232602.0
totalCurrentLiabilities       290945308.0  274274837.0  267978614.0  281813550.0
otherStockholderEquity        -37235569.0  -37594335.0  -37559847.0  -37430740.0
propertyPlantEquipment         72322155.0   76353429.0   78921393.0   84591774.0
totalCurrentAssets             67019214.0   69395520.0   75407150.0   80340589.0
longTermInvestments            38000000.0   38000000.0   38000000.0   38000000.0
netTangibleAssets            -128711921.0 -111867217.0 -100338649.0 -102262743.0
netReceivables                   405869.0     352000.0    1069267.0     500000.0
otherCurrentAssets                    NaN          NaN    2998522.0          NaN
deferredLongTermAssetCharges          NaN          NaN          NaN    2665776.0

quote---------------------------------------------------------
                                           2022-11-11
Breakdown                                            
1y Target Est                                    20.0
52 Week Range                         0.8800 - 2.9400
Ask                                      1.7500 x 900
Avg. Volume                                   32045.0
Beta (5Y Monthly)                                1.12
Bid                                     1.6500 x 4000
Day's Range                           1.6638 - 1.8391
EPS (TTM)                                      -0.153
Earnings Date             Nov 11, 2022 - Nov 14, 2022
Ex-Dividend Date                         Aug 27, 2018
Forward Dividend & Yield                    N/A (N/A)
Market Cap                                    52.205M
Open                                             1.83
PE Ratio (TTM)                                    NaN
Previous Close                                    1.8
Quote Price                                    1.6638
Volume                                        17381.0
"""
