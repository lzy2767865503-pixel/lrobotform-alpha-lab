import unittest

from lrobotform_alpha.alpha import cronbach_alpha


class CronbachAlphaTests(unittest.TestCase):
    def test_perfectly_aligned_items_have_high_alpha(self):
        matrix = [
            [1, 1, 1],
            [2, 2, 2],
            [3, 3, 3],
            [4, 4, 4],
            [5, 5, 5],
        ]
        self.assertAlmostEqual(cronbach_alpha(matrix), 1.0, places=6)

    def test_single_item_is_not_applicable(self):
        self.assertIsNone(cronbach_alpha([[1], [2], [3]]))


if __name__ == "__main__":
    unittest.main()
