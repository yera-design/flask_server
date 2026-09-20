import math

# Worst-case operation-count formulas, not literal execution: e.g. bubble_sort
# at n_max=10,000 sampled every step=10 would mean actually looping ~1000
# times over inputs up to size 10,000 (billions of ops) — infeasible to run
# live in a request. The formulas give the exact same growth curve instantly.


def _linear_search(n):
    return n


def _binary_search(n):
    return math.log2(n + 1) if n > 0 else 0


def _bubble_sort(n):
    return n * (n - 1)


def _selection_sort(n):
    return n * (n - 1) / 2 + max(n - 1, 0)


def _insertion_sort(n):
    return n * (n - 1) / 2


def _merge_sort(n):
    return n * math.log2(n) if n > 0 else 0


def _quick_sort(n):
    return n * math.log2(n) if n > 0 else 0


def _nested_loops(n):
    return n * n


# name -> (Big-O label, worst-case operation-count formula)
ALGORITHMS = {
    "linear_search": ("O(n)", _linear_search),
    "binary_search": ("O(log n)", _binary_search),
    "bubble_sort": ("O(n^2)", _bubble_sort),
    "nested_loops": ("O(n^2)", _nested_loops),
    "selection_sort": ("O(n^2)", _selection_sort),
    "insertion_sort": ("O(n^2)", _insertion_sort),
    "merge_sort": ("O(n log n)", _merge_sort),
    "quick_sort": ("O(n log n)", _quick_sort),
}
