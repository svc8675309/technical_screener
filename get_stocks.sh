#!/bin/bash
python run_get_exchanges.py
for i in {0..26}
do
    python run_get_stocks.py -a $i &
done