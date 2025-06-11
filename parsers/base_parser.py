# parsers/base_parser.py

from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, message):
        """
        Each parser must implement this method to parse the incoming message.

        :param message: str
        :return: dict (parsed data)
        """
        pass
