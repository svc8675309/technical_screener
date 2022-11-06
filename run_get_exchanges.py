import sys, getopt
from stock.data_gather.stock_data import StockData
from yahoo_fin import stock_info as si
import os
import pandas as pd


def main():
    '''
    gets exchanges and save them to a csv
    '''
    resource_dir: str = "./data/resource"
    
    if not os.path.exists(resource_dir):
        # need to pull data
        os.makedirs(resource_dir)

    tickers = si.tickers_nasdaq()
    
    # save the tickers
    df = pd.DataFrame(tickers)
    df.to_csv(f"{resource_dir}/nasdaq.csv", header=False, index=False)

    # prove that it can be loaded
    with open(f"{resource_dir}/nasdaq.csv") as f:
        lines = f.read().splitlines()
    print(lines)    

if __name__ == "__main__":
    main()
