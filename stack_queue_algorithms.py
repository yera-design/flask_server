from data_structures import Queue, Stack

MATCHING_BRACKETS = {")": "(", "]": "[", "}": "{"}


def is_balanced(expression):
    """Check that all brackets in expression are properly matched."""
    stack = Stack()
    for char in expression:
        if char in "([{":
            stack.push(char)
        elif char in ")]}":
            if stack.is_empty() or stack.pop() != MATCHING_BRACKETS[char]:
                return False
    return stack.is_empty()


def reverse_string(text):
    """Reverse text using a Stack."""
    stack = Stack()
    for char in text:
        stack.push(char)

    reversed_chars = []
    while not stack.is_empty():
        reversed_chars.append(stack.pop())
    return "".join(reversed_chars)


def is_palindrome(text):
    """Check if text reads the same forwards and backwards."""
    stack = Stack()
    queue = Queue()
    for char in text:
        stack.push(char)
        queue.enqueue(char)

    while not stack.is_empty():
        if stack.pop() != queue.dequeue():
            return False
    return True


def generate_binary_numbers(n):
    """Return binary representations of 1..n using a Queue."""
    if n <= 0:
        return []

    results = []
    queue = Queue()
    queue.enqueue("1")

    for _ in range(n):
        current = queue.dequeue()
        results.append(current)
        queue.enqueue(current + "0")
        queue.enqueue(current + "1")

    return results

