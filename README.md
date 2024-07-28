### Assumptions
You use the apis 'in real time'. Aka imagine we had websockets to data providers and we would call `SwapTokenServer.cache_exchange_rate` whenever we get the most up to date exchange rates. Then when 
a user uses our front-end our api server will call `SwapTokenServer.swap_route` to determine the optimal route.

### Explanation
I have two classes, `SwapTokenOptimizedService` and `SwapTokenBruteForceService`. 
`SwapTokenBruteForceService` uses a brute force approach to find the best route where as `SwapTokenOptimizedService` uses a graph and dijkstra's algorithm to find the best route.
They both implement an interface called `SwapTokenServiceInterface` which has two methods:
* `cache_exchange_rate` which is called whenever someone swaps onchain.
* `swap_route` which is called when we want to find the optimal route using cached exchange rates.

I did not spend a lot of time on `SwapTokenBruteForceService` which is why it is not very readable and messy.

### Tests
I wrote unit test cases to test both services. There is one failing test in `SwapTokenBruteForceService` that I ran out of time to fix. Essentially the bug is that `SwapTokenBruteForceService` only takes into account one exchange rate `a/b` and not `b/a`. 

I have two screenshots to add context to two of the test cases whose scenario is more complex:
* `test_given_graph_with_four_route_being_best_when_calling_swap_route_then_return_best_three_route` https://github.com/yawhide/Fun-with-swaps/blob/5d9a1ab0a4205728c5b3bc31d43582550c729e1e/four_route_test_case.png
* `test_given_four_dex_and_many_tokens_when_calling_swap_route_then_return_correct_three_route` & 
`test_given_four_dex_and_many_tokens_when_calling_swap_route_then_return_correct_two_route` https://github.com/yawhide/Fun-with-swaps/blob/5d9a1ab0a4205728c5b3bc31d43582550c729e1e/complex_test_case.png

To run the tests:
```python
python3 -m unittest discover -p "*_test.py"
```

### Benchmark
I wrote a simple benchmark script to showcase the speed difference. I generate 275,814 exchange rates across 7 decentralized exchanges and 199 cryptocurrencies. The graph based service is ~400x faster in my one benchmark!

To run the benchmarking script:
```python
python3 benchmark.py
```
