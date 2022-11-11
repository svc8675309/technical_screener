import unittest
from stock.data_gather.balance_income import BalanceIncome
from datetime import date


class BalanceSheetTest(unittest.TestCase):
    """
    python -m unittest tests
    python -m unittest tests.balance_sheet_test
    python -m unittest tests.balance_sheet_test.BalanceSheetTest
    python -m unittest tests.balance_sheet_test.BalanceSheetTest.test_roe
    
    Args:
        unittest (_type_): _description_
    """
    
    __wmt:BalanceIncome = None

    def setUp(self):
        self.__wmt = BalanceIncome("WMT",date.today())

    def test_roe(self):
        ret = self.__wmt.get_return_on_equity()
        print(ret)  

if __name__=="__main__":
    unittest.main() 
