from abc import ABC, abstractmethod
from decimal import Decimal

from models.cryptocurrency import Cryptocurrency
from models.decentalized_exchanges import DecentalizedExchange


class SwapTokenServiceInterface(ABC):
    @abstractmethod
    def cache_exchange_rate(
        self,
        dex: DecentalizedExchange,
        token_sold: Cryptocurrency,
        token_bought: Cryptocurrency,
        exchange_rate: Decimal | float,
    ):
        raise NotImplementedError

    @abstractmethod
    def swap_route(
        self,
        token_sold: Cryptocurrency,
        token_bought: Cryptocurrency,
        amount_sold: Decimal,
    ):
        raise NotImplementedError
