import sys, getopt
from stock.data_gather.stock_data import StockData
from yahoo_fin import stock_info as si
from stock.data_gather.balance_income import BalanceIncome

def main(argv):
    """
    python run_get_stocks.py -a 1 - 26
    Meaning get groups of tickers starting with a character 1 - 26
    """

    try:
        opts, args = getopt.getopt(argv, "ha:", ["Help", "AlphaNum"])
    except getopt.GetoptError:
        print("run_get_stocks.py -a < 1-26 >")
        sys.exit(2)
    # if not set then get all tickers serially
    AlphaNum = -1
    for opt, arg in opts:
        if opt in ("-a", "--AlphaNum") and arg.isalnum():
            AlphaNum = int(arg)

    # Read the tickers
    resource_dir: str = "./data/resource"
    with open(f"{resource_dir}/nasdaq.csv") as f:
        lines = f.read().splitlines()

    two_d_array = StockData.group_by_char(lines)

    if AlphaNum < 0 or AlphaNum > 26:
        count = 0
        for tickers in two_d_array:
            print(count)
            StockData.get_data(tickers)
#            BalanceIncome.get_data(tickers)
            count = count + 1
    else:
        StockData.get_data(two_d_array[AlphaNum])
#        BalanceIncome.get_data(two_d_array[AlphaNum])

    print(f"AlphaNum-{AlphaNum} : complete")    

if __name__ == "__main__":
    main(sys.argv[1:])
