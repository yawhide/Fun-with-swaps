from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from decimal import Decimal

from models.cryptocurrency import Cryptocurrency
from models.decentalized_exchanges import DecentalizedExchange
from services.swap_token_service_interface import SwapTokenServiceInterface


@dataclass
class WeightedEdge:
    weight: Decimal
    dex: DecentalizedExchange


@dataclass
class Node:
    cryptocurrency: Cryptocurrency
    adjacency_dict: dict[Node, WeightedEdge] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.cryptocurrency)

    def __repr__(self) -> str:
        return f"Node({self.cryptocurrency.value})"

    def __lt__(self, other: Node) -> bool:
        return self.cryptocurrency.value <= other.cryptocurrency.value


def print_path(path: list[Node]):
    if path:
        print(" -> ".join(node.cryptocurrency.value for node in path))
    else:
        print("No path found")


def print_graph(nodes: list[Node]) -> None:
    for node in nodes:
        print(node)
        for neighbor, weighted_edge in node.adjacency_dict.items():
            print(f"  -> {neighbor.cryptocurrency.value} ({weighted_edge})")
        print()


class SwapTokenOptimizedService(SwapTokenServiceInterface):
    def __init__(self):
        # dex -> cryptocurrency -> node
        self.graph: dict[Cryptocurrency, Node] = {}

    def cache_exchange_rate(
        self,
        dex: DecentalizedExchange,
        token_sold: Cryptocurrency,
        token_bought: Cryptocurrency,
        exchange_rate: Decimal,
    ):
        """Caches trades for a given token pair for a given dex.
        Eg

        Args:
            dex (str): The decentralized exchange
            token_a (str): ticker for token sold
            token_b (str): ticker for token bought
            exchange_rate (Decimal): the exchange rate for the trade
        """
        exchange_rate = Decimal(str(exchange_rate))
        token_sold_node = self.graph.get(token_sold)
        if not token_sold_node:
            self.graph[token_sold] = Node(token_sold)
            token_sold_node = self.graph[token_sold]
        token_bought_node = self.graph.get(token_bought)
        if not token_bought_node:
            self.graph[token_bought] = Node(token_bought)
            token_bought_node = self.graph[token_bought]

        if token_sold_node.adjacency_dict.get(token_bought_node):
            # if the edge already exists, we update the weight (which is the exchange rate)
            existing_weight = token_sold_node.adjacency_dict[token_bought_node].weight
            if exchange_rate > existing_weight:
                token_sold_node.adjacency_dict[token_bought_node] = WeightedEdge(
                    exchange_rate, dex
                )
                token_bought_node.adjacency_dict[token_sold_node] = WeightedEdge(
                    1 / exchange_rate, dex
                )
        else:
            # add edge
            token_sold_node.adjacency_dict[token_bought_node] = WeightedEdge(
                exchange_rate, dex
            )
            token_bought_node.adjacency_dict[token_sold_node] = WeightedEdge(
                1 / exchange_rate, dex
            )

    def _dijkstra(
        self, start_node: Node, target_node: Node, depth_limit: int = 3
    ) -> tuple[list[Node], Decimal]:
        queue: list[tuple[Decimal, Node]] = []
        distances = {start_node: Decimal(1)}
        heapq.heappush(queue, (Decimal(1), start_node))
        paths = {start_node: [start_node]}

        while queue:
            current_distance, current_node = heapq.heappop(queue)

            if len(paths[current_node]) > depth_limit:
                continue

            if current_node == target_node:
                continue

            for neighbor, weighted_edge in current_node.adjacency_dict.items():
                new_distance = current_distance * weighted_edge.weight
                new_path = paths[current_node] + [neighbor]

                if neighbor not in distances or new_distance > distances[neighbor]:
                    distances[neighbor] = new_distance
                    paths[neighbor] = new_path
                    heapq.heappush(queue, (new_distance, neighbor))

        return paths.get(target_node, None), distances.get(target_node, Decimal("inf"))

    def _build_route(self, path: list[Node]) -> list[DecentalizedExchange]:
        route = []
        index = 0
        while index < len(path) - 1:
            current_node = path[index]
            weighted_edge = self.graph[current_node.cryptocurrency].adjacency_dict[
                path[index + 1]
            ]
            route.append(weighted_edge.dex)
            index += 1
        return route

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
        if token_sell not in self.graph or token_buy not in self.graph:
            raise ValueError("No route found")
        token_sell_node = self.graph[token_sell]
        token_buy_node = self.graph[token_buy]
        path, exchange_rate = self._dijkstra(token_sell_node, token_buy_node)
        route = self._build_route(path)
        return route, exchange_rate * amount_sell
