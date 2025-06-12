# tests/test_parsers.py

import unittest
from parsers.upi_parser import UPIParser
from parsers.credit_card_parser import CreditCardParser
from parsers.salary_parser import SalaryParser
from parsers.parser_factory import get_parser

class TestParsers(unittest.TestCase):

    def test_upi_parser(self):
        message = "Sent Rs.115.00 From HDFC Bank A/C *5000 To Raj sweets \n On 09/06/25"
        parser = get_parser(message)
        parsed = parser.parse(message)
        self.assertEqual(parsed['Date'], '09/06/2025')
        self.assertEqual(parsed['Account'], '(p)HDFC')
        self.assertTrue(parsed['Category'])
        self.assertTrue(parsed['Subcategory'])
        self.assertEqual(parsed['Note'], 'Raj sweets')
        self.assertEqual(parsed['Amount'], 115.00)
        self.assertEqual(parsed['Income/Expense'], 'Expense')

    def test_credit_card_parser(self):
        message = "Rs.560.00 spent on your SBI Credit Card ending 7752 at MILANO ICE CREAM on 09/06/25."
        parser = get_parser(message)
        parsed = parser.parse(message)
        self.assertEqual(parsed['Date'], '09/06/2025')
        self.assertEqual(parsed['Account'], 'SBI creditcard')
        self.assertTrue(parsed['Category'])
        self.assertTrue(parsed['Subcategory'])
        self.assertEqual(parsed['Note'], 'MILANO ICE CREAM')
        self.assertEqual(parsed['Amount'], 560.00)
        self.assertEqual(parsed['Income/Expense'], 'Expense')

    def test_salary_parser(self):
        message = "Update! INR 1,23,450.00 deposited in HDFC Bank A/c XX5000 on 30-MAY-25 for NEFT Cr-HSBC0400002"
        parser = get_parser(message)
        parsed = parser.parse(message)
        self.assertEqual(parsed['Date'], '30/05/2025')
        self.assertEqual(parsed['Account'], '(p)HDFC')
        self.assertEqual(parsed['Category'], 'Salary')
        self.assertEqual(parsed['Subcategory'], '')
        self.assertEqual(parsed['Income/Expense'], 'Income')
        self.assertEqual(parsed['Amount'], 123450.00)

    def test_unknown_parser(self):
        message = "Random message that does not match"
        parser = get_parser(message)
        self.assertIsNone(parser)

if __name__ == '__main__':
    unittest.main()
