import unittest
from category_predictor.category_predictor import CategoryPredictor

class TestCategoryPredictor(unittest.TestCase):
    def test_category_1(self):
        predictor = CategoryPredictor()
        category, subcategory = predictor.predict("Avenue super mart")
        self.assertEqual(category,"Food and others")
        self.assertEqual(subcategory,"Groceries and household items")
    def test_category_2(self):
        predictor = CategoryPredictor()
        category, subcategory = predictor.predict("Neptunes")
        self.assertEqual(category,"Education")
        self.assertEqual(subcategory,"co curricular")
    def test_category_3(self):
        predictor = CategoryPredictor()
        category, subcategory = predictor.predict("Xander health llp")
        self.assertEqual(category,"Health")
        self.assertEqual(subcategory,"Hospital")


if __name__ == '__main__':
    unittest.main()
