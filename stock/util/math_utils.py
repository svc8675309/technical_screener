import numpy as np


class MathUtils(object):
    """
    Utility functions
    """

    @staticmethod
    def best_fit_slope(y: list):
        """_summary_ find a slope given an array

        Args:
            y (list): _description_ list of times

        Returns:
            _type_: _description_ return the slope
        """
        if len(y) > 1:
            # Calculate the best fit slope
            x = np.arange(1, len(y) + 1)
            m = ((np.mean(x) * np.mean(y)) - np.mean(x * y)) / (
                (np.mean(x) ** 2) - np.mean(x ** 2)
            )
            return m
        else:
            return 0
