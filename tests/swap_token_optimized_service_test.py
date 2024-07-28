from unittest import TestCase

from services.swap_token_optimized_service import SwapTokenOptimizedService
from tests.base_swap_token_service_tests import BaseSwapTokenServiceTests


class TestSwapTokenOptimizedService(BaseSwapTokenServiceTests, TestCase):
    def get_service(self) -> SwapTokenOptimizedService:
        return SwapTokenOptimizedService()
