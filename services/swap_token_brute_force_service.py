from collections import defaultdict
from decimal import Decimal
from operator import itemgetter

from models.cryptocurrency import Cryptocurrency
from models.decentalized_exchanges import DecentalizedExchange
from services.swap_token_service_interface import SwapTokenServiceInterface


class SwapTokenBruteForceService(SwapTokenServiceInterface):
    def __init__(self):
        # dex -> token_a (sell 1) -> token_b (buy n) -> exchange_rate
        self.dex_exchange_rates: defaultdict[
            DecentalizedExchange,
            defaultdict[Cryptocurrency, defaultdict[Cryptocurrency, Decimal]],
        ] = defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal)))

    def cache_exchange_rate(
        self,
        dex: DecentalizedExchange,
        token_sold: Cryptocurrency,
        token_bought: Cryptocurrency,
        exchange_rate: Decimal | float,
    ):
        """Caches trades for a given token pair for a given dex.
        Eg

        Args:
            dex (str): The decentralized exchange
            token_a (str): ticker for token sold
            token_b (str): ticker for token bought
            exchange_rate (Decimal): the exchange rate for the trade
        """
        self.dex_exchange_rates[dex][token_sold][token_bought] = Decimal(
            str(exchange_rate)
        )

    def _sell_token(
        self,
        token_sell: Cryptocurrency,
        token_buy: Cryptocurrency,
        amount_sell: Decimal,
    ) -> tuple[list[DecentalizedExchange], Decimal]:
        most_token_to_buy = Decimal(0)
        result: tuple[list[DecentalizedExchange], Decimal] = [
            DecentalizedExchange.WHIRLPOOL,
            Decimal(0),
        ]
        for dex, all_exchange_rates in self.dex_exchange_rates.items():
            exchange_rate = all_exchange_rates[token_sell][token_buy]
            amount_to_buy = exchange_rate * amount_sell
            if amount_to_buy > most_token_to_buy:
                most_token_to_buy = amount_to_buy
                result = ([dex], amount_to_buy)
        return result

    def swap_route(
        self,
        token_sell: Cryptocurrency,
        token_buy: Cryptocurrency,
        amount_sell: Decimal,
    ) -> tuple[list[DecentalizedExchange], Decimal]:
        """Returns the route with the best exchange rate

        Args:
            token_sell (str): ticker for token you will sell
            token_buy (str): ticket for token you will buy
            amount_sell (Decimal): quantity of token to sell

        Returns:
            tuple[list[str], Decimal]: A tuple containing:
                - list[str]: The route of decentralized exchanges to get from token_sell to token_buy
                - Decimal: The amount of token_buy received after the exchange
        """
        # 1 hop
        one_hop_result = self._sell_token(token_sell, token_buy, amount_sell)
        # 2 hop
        most_token_to_buy = Decimal(0)
        two_hop_result: tuple[list[DecentalizedExchange], Decimal] | None = None
        for dex, all_exchange_rates in self.dex_exchange_rates.items():
            if first_hop_exchange_rates := all_exchange_rates.get(token_sell):
                for (
                    first_hop_token_to_buy,
                    first_hop_exchange_rate,
                ) in first_hop_exchange_rates.items():
                    if first_hop_token_to_buy == token_buy:
                        continue
                    second_hop_token_to_sell = first_hop_token_to_buy
                    second_hop_amount_to_sell = amount_sell * first_hop_exchange_rate
                    two_hop_dex, current_amount_to_buy = self._sell_token(
                        second_hop_token_to_sell, token_buy, second_hop_amount_to_sell
                    )
                    if current_amount_to_buy > most_token_to_buy:
                        most_token_to_buy = current_amount_to_buy
                        two_hop_result = ([dex] + two_hop_dex, current_amount_to_buy)
        # 3 hop
        most_token_to_buy = Decimal(0)
        three_hop_result: tuple[list[DecentalizedExchange], Decimal] | None = None
        for dex, all_exchange_rates in self.dex_exchange_rates.items():
            if first_hop_exchange_rates := all_exchange_rates.get(token_sell):
                for (
                    first_hop_token_to_buy,
                    first_hop_exchange_rate,
                ) in first_hop_exchange_rates.items():
                    if first_hop_token_to_buy == token_buy:
                        continue
                    second_hop_token_to_sell = first_hop_token_to_buy
                    second_hop_amount_to_sell = amount_sell * first_hop_exchange_rate
                    for (
                        two_hop_dex,
                        second_hop_exchange_rates,
                    ) in self.dex_exchange_rates.items():
                        if second_hop_exchange_rates := second_hop_exchange_rates.get(
                            second_hop_token_to_sell
                        ):
                            for (
                                second_hop_token_to_buy,
                                second_hop_exchange_rate,
                            ) in second_hop_exchange_rates.items():
                                if second_hop_token_to_buy == token_buy:
                                    continue
                                third_hop_token_to_sell = second_hop_token_to_buy
                                third_hop_amount_to_sell = (
                                    second_hop_amount_to_sell * second_hop_exchange_rate
                                )
                                three_hop_dex, current_amount_to_buy = self._sell_token(
                                    third_hop_token_to_sell,
                                    token_buy,
                                    third_hop_amount_to_sell,
                                )
                                if current_amount_to_buy > most_token_to_buy:
                                    most_token_to_buy = current_amount_to_buy
                                    three_hop_result = (
                                        [dex, two_hop_dex] + three_hop_dex,
                                        current_amount_to_buy,
                                    )
        # Filter out None values
        routes = [
            hop
            for hop in [one_hop_result, two_hop_result, three_hop_result]
            if hop and hop[1] > Decimal(0)
        ]
        if routes:
            return max(routes, key=itemgetter(1))
        else:
            raise ValueError("No route found")
