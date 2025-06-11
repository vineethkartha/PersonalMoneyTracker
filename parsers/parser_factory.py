# parsers/parser_factory.py

from .upi_parser import UPIParser
from .credit_card_parser import CreditCardParser
from .salary_parser import SalaryParser

def get_parser(message):
    """
    Determines the correct parser based on message patterns.
    """
    if "UPI" in message or "From HDFC Bank A/C" in message:
        return UPIParser()
    elif "Credit Card ending" in message:
        return CreditCardParser()
    elif "deposited in HDFC Bank A/c" in message:
        return SalaryParser()
    else:
        return None
