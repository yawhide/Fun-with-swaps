from decimal import Decimal

from models.cryptocurrency import Cryptocurrency
from models.decentalized_exchanges import DecentalizedExchange
from services.swap_token_service_interface import SwapTokenServiceInterface
from tests.fixtures.generated_dex_exchange_rates import generate_data


class BaseSwapTokenServiceTests:
    def get_service(self) -> SwapTokenServiceInterface:
        raise NotImplementedError

    def test_given_single_dex_when_calling_swap_route_with_cryptocurrencies_with_no_liquidity_raise_error(
        self,
    ):
        service = self.get_service()
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.USDC,
            Cryptocurrency.SOL,
            Decimal("0.005"),
        )
        with self.assertRaises(ValueError):
            service.swap_route(Cryptocurrency.USDC, Cryptocurrency.BONK, Decimal(10))

    def test_given_single_dex_when_calling_swap_route_return_dex_and_exchange_rate(
        self,
    ):
        service = self.get_service()
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.USDC,
            Cryptocurrency.SOL,
            Decimal("0.005"),
        )
        self.assertEqual(
            service.swap_route(Cryptocurrency.USDC, Cryptocurrency.SOL, Decimal(10)),
            ([DecentalizedExchange.RAYDIUM], Decimal("0.05")),
        )

    def test_given_single_dex_when_calling_swap_route_then_return_two_hop_route(
        self,
    ):
        service = self.get_service()
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.USDC,
            Cryptocurrency.SOL,
            Decimal("0.005"),
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.USDC,
            Cryptocurrency.WIF,
            Decimal("0.4"),
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.WIF,
            Cryptocurrency.SOL,
            Decimal("0.0135"),
        )
        self.assertEqual(
            service.swap_route(Cryptocurrency.USDC, Cryptocurrency.SOL, Decimal(10)),
            (
                [DecentalizedExchange.RAYDIUM, DecentalizedExchange.RAYDIUM],
                Decimal("0.05400"),
            ),
        )

    def test_given_single_dex_when_calling_swap_route_then_return_three_hop_route(
        self,
    ):
        service = self.get_service()
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.USDC,
            Cryptocurrency.SOL,
            Decimal("0.005"),
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.USDC,
            Cryptocurrency.WIF,
            Decimal("0.4"),
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.WIF,
            Cryptocurrency.SOL,
            Decimal("0.0135"),
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.WIF,
            Cryptocurrency.JUP,
            Decimal("2.252"),
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.JUP,
            Cryptocurrency.SOL,
            Decimal("0.0065"),
        )
        self.assertEqual(
            service.swap_route(Cryptocurrency.USDC, Cryptocurrency.SOL, Decimal(10)),
            (
                [
                    DecentalizedExchange.RAYDIUM,
                    DecentalizedExchange.RAYDIUM,
                    DecentalizedExchange.RAYDIUM,
                ],
                Decimal("0.05855200"),
            ),
        )

    def test_given_many_dex_when_calling_swap_route_return_dex_and_exchange_rate(
        self,
    ):
        service = self.get_service()
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.USDC,
            Cryptocurrency.SOL,
            Decimal("0.005"),
        )
        self.assertEqual(
            service.swap_route(Cryptocurrency.USDC, Cryptocurrency.SOL, Decimal(10)),
            ([DecentalizedExchange.RAYDIUM], Decimal("0.05")),
        )

    def test_given_many_dex_when_calling_swap_route_then_return_two_hop_route(
        self,
    ):
        service = self.get_service()
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.USDC,
            Cryptocurrency.SOL,
            Decimal("0.005"),
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.USDC,
            Cryptocurrency.WIF,
            Decimal("0.4"),
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.WIF,
            Cryptocurrency.SOL,
            Decimal("0.0135"),
        )
        self.assertEqual(
            service.swap_route(Cryptocurrency.USDC, Cryptocurrency.SOL, Decimal(10)),
            (
                [DecentalizedExchange.RAYDIUM, DecentalizedExchange.RAYDIUM],
                Decimal("0.05400"),
            ),
        )

    def test_given_many_dex_when_calling_swap_route_then_return_three_hop_route(
        self,
    ):
        service = self.get_service()
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.USDC,
            Cryptocurrency.SOL,
            Decimal("0.005"),
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.USDC,
            Cryptocurrency.WIF,
            Decimal("0.4"),
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.WIF,
            Cryptocurrency.SOL,
            Decimal("0.0135"),
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.WIF,
            Cryptocurrency.JUP,
            Decimal("2.252"),
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM,
            Cryptocurrency.JUP,
            Cryptocurrency.SOL,
            Decimal("0.0065"),
        )
        self.assertEqual(
            service.swap_route(Cryptocurrency.USDC, Cryptocurrency.SOL, Decimal(10)),
            (
                [
                    DecentalizedExchange.RAYDIUM,
                    DecentalizedExchange.RAYDIUM,
                    DecentalizedExchange.RAYDIUM,
                ],
                Decimal("0.05855200"),
            ),
        )

    def test_given_four_dex_and_many_tokens_when_calling_swap_route_then_return_correct_three_route(
        self,
    ):
        service = self.get_service()
        service.cache_exchange_rate(
            DecentalizedExchange.OPEN_BOOK, Cryptocurrency.W, Cryptocurrency.LOCKIN, 10
        )
        service.cache_exchange_rate(
            DecentalizedExchange.WHIRLPOOL, Cryptocurrency.W, Cryptocurrency.BABY, 0.2
        )
        service.cache_exchange_rate(
            DecentalizedExchange.WHIRLPOOL, Cryptocurrency.W, Cryptocurrency.ATLAS, 1.2
        )
        service.cache_exchange_rate(
            DecentalizedExchange.OPEN_BOOK, Cryptocurrency.W, Cryptocurrency.BAT, 1.1
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM, Cryptocurrency.LOCKIN, Cryptocurrency.BAT, 0.5
        )
        service.cache_exchange_rate(
            DecentalizedExchange.WHIRLPOOL, Cryptocurrency.BABY, Cryptocurrency.BAT, 0.2
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM, Cryptocurrency.BABY, Cryptocurrency.FIDA, 5
        )
        service.cache_exchange_rate(
            DecentalizedExchange.LIFINITY, Cryptocurrency.ATLAS, Cryptocurrency.BAT, 0.2
        )
        service.cache_exchange_rate(
            DecentalizedExchange.OPEN_BOOK,
            Cryptocurrency.FIDA,
            Cryptocurrency.ATLAS,
            0.05,
        )
        self.assertEqual(
            service.swap_route(Cryptocurrency.BAT, Cryptocurrency.BABY, Decimal(2)),
            (
                [
                    DecentalizedExchange.LIFINITY,
                    DecentalizedExchange.OPEN_BOOK,
                    DecentalizedExchange.RAYDIUM,
                ],
                Decimal(40),  # 2 * 5 * 20 * 0.2 = 40
            ),
        )

    def test_given_four_dex_and_many_tokens_when_calling_swap_route_then_return_correct_two_route(
        self,
    ):
        service = self.get_service()
        service.cache_exchange_rate(
            DecentalizedExchange.OPEN_BOOK, Cryptocurrency.W, Cryptocurrency.LOCKIN, 10
        )
        service.cache_exchange_rate(
            DecentalizedExchange.WHIRLPOOL, Cryptocurrency.W, Cryptocurrency.BABY, 0.2
        )
        service.cache_exchange_rate(
            DecentalizedExchange.WHIRLPOOL, Cryptocurrency.W, Cryptocurrency.ATLAS, 1.2
        )
        service.cache_exchange_rate(
            DecentalizedExchange.OPEN_BOOK, Cryptocurrency.W, Cryptocurrency.BAT, 1.1
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM, Cryptocurrency.LOCKIN, Cryptocurrency.BAT, 0.5
        )
        service.cache_exchange_rate(
            DecentalizedExchange.WHIRLPOOL, Cryptocurrency.BABY, Cryptocurrency.BAT, 0.2
        )
        service.cache_exchange_rate(
            DecentalizedExchange.RAYDIUM, Cryptocurrency.BABY, Cryptocurrency.FIDA, 5
        )
        service.cache_exchange_rate(
            DecentalizedExchange.LIFINITY, Cryptocurrency.ATLAS, Cryptocurrency.BAT, 0.2
        )
        service.cache_exchange_rate(
            DecentalizedExchange.OPEN_BOOK,
            Cryptocurrency.FIDA,
            Cryptocurrency.ATLAS,
            0.05,
        )
        self.assertEqual(
            service.swap_route(Cryptocurrency.W, Cryptocurrency.BAT, Decimal(2)),
            (
                [DecentalizedExchange.OPEN_BOOK, DecentalizedExchange.RAYDIUM],
                Decimal(10),  # 2 * 10 * 0.5 = 10
            ),
        )

    def test_given_graph_with_four_route_being_best_when_calling_swap_route_then_return_best_three_route(
        self,
    ):
        service = self.get_service()
        service.cache_exchange_rate(
            DecentalizedExchange.OPEN_BOOK, Cryptocurrency.ACS, Cryptocurrency.BABY, 2
        )
        service.cache_exchange_rate(
            DecentalizedExchange.OPEN_BOOK, Cryptocurrency.ACS, Cryptocurrency.DADDY, 2
        )
        service.cache_exchange_rate(
            DecentalizedExchange.OPEN_BOOK, Cryptocurrency.BABY, Cryptocurrency.C98, 2
        )
        service.cache_exchange_rate(
            DecentalizedExchange.OPEN_BOOK, Cryptocurrency.C98, Cryptocurrency.DADDY, 2
        )
        service.cache_exchange_rate(
            DecentalizedExchange.LIFINITY, Cryptocurrency.ELON, Cryptocurrency.DADDY, 50
        )
        service.cache_exchange_rate(
            DecentalizedExchange.LIFINITY, Cryptocurrency.C98, Cryptocurrency.ELON, 2
        )
        self.assertEqual(
            service.swap_route(Cryptocurrency.ACS, Cryptocurrency.DADDY, Decimal(2)),
            (
                [
                    DecentalizedExchange.OPEN_BOOK,
                    DecentalizedExchange.OPEN_BOOK,
                    DecentalizedExchange.OPEN_BOOK,
                ],
                Decimal(16),  # 2 * 2 * 2 * 2 = 16
            ),
        )

    def test_given_a_lot_of_exchange_rates_with_open_book_having_best_rates_when_calling_swap_route_then_return_route_only_using_open_book(
        self,
    ):
        service = self.get_service()
        generate_data(service)
        actual_route, actual_tokens_bought = service.swap_route(
            Cryptocurrency.USDC, Cryptocurrency.SOL, Decimal(10)
        )
        self.assertEqual(
            actual_route,
            [
                DecentalizedExchange.OPEN_BOOK,
                DecentalizedExchange.OPEN_BOOK,
                DecentalizedExchange.OPEN_BOOK,
            ],
        )
        self.assertAlmostEqual(
            actual_tokens_bought, Decimal("0.05515585003844906898694841516"), places=8
        )
