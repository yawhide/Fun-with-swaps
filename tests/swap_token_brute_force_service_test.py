from unittest import TestCase

from services.swap_token_brute_force_service import SwapTokenBruteForceService
from tests.base_swap_token_service_tests import BaseSwapTokenServiceTests


class TestSwapTokenBruteForceService(BaseSwapTokenServiceTests, TestCase):
    def get_service(self) -> SwapTokenBruteForceService:
        return SwapTokenBruteForceService()
