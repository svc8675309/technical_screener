import unittest
from stock.data_gather.balance_income import BalanceIncome
from stock.data_gather.quote import Quote
from datetime import date


class FinancialsTest(unittest.TestCase):
    """
    python -m unittest tests
    python -m unittest tests.balance_sheet_test
    python -m unittest tests.balance_sheet_test.FinancialsTest
    python -m unittest tests.balance_sheet_test.FinancialsTest.test_roe

    Args:
        unittest (_type_): _description_
    """

    __bi: BalanceIncome = None
    __q: Quote = None

    def setUp(self):
        self.__bi = BalanceIncome("WMT", date.today())
        self.__q = Quote("WMT", date.today())

    def test_roe(self):
        ret = self.__bi.get_return_on_equity()
        print(ret)

    def test_pe(self):
        ret = self.__q.get_price_per_earnings()
        print(ret)


if __name__ == "__main__":
    unittest.main()
