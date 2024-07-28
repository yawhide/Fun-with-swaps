import time
from decimal import Decimal

from models.cryptocurrency import Cryptocurrency
from services.swap_token_brute_force_service import SwapTokenBruteForceService
from services.swap_token_optimized_service import SwapTokenOptimizedService
from tests.fixtures.generated_dex_exchange_rates import generate_data


def simple_benchmark(service):
    generate_data(service)
    now = time.monotonic()
    service.swap_route(Cryptocurrency.USDC, Cryptocurrency.SOL, Decimal(10))
    print(
        f"Service used: {service.__class__.__name__}, time taken: {time.monotonic() - now:.2f}s"
    )


simple_benchmark(SwapTokenBruteForceService())
simple_benchmark(SwapTokenOptimizedService())
