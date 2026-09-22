import math

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


def _stack_push_pop(n):
    return 2 * n


def _queue_enqueue_dequeue(n):
    return 2 * n


def _queue_dequeue_naive(n):
    return n * (n + 1) / 2


def _balanced_parentheses(n):
    return n


def _reverse_string(n):
    return 2 * n


def _is_palindrome(n):
    return 4 * n


def _generate_binary_numbers(n):
    return 3 * n


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
    "stack_push_pop": ("O(n)", _stack_push_pop),
    "queue_enqueue_dequeue": ("O(n)", _queue_enqueue_dequeue),
    "queue_dequeue_naive": ("O(n^2)", _queue_dequeue_naive),
    "balanced_parentheses": ("O(n)", _balanced_parentheses),
    "reverse_string": ("O(n)", _reverse_string),
    "is_palindrome": ("O(n)", _is_palindrome),
    "generate_binary_numbers": ("O(n)", _generate_binary_numbers),
}

