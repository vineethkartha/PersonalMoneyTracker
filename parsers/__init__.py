# parsers/__init__.py

from .base_parser import BaseParser
from .upi_parser import UPIParser
from .credit_card_parser import CreditCardParser
from .salary_parser import SalaryParser
from .parser_factory import get_parser

