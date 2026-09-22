from collections import deque


class EmptyStackError(Exception):
    pass


class EmptyQueueError(Exception):
    pass


class Stack:
    """LIFO stack backed by a list."""

    def __init__(self, items=None):
        self._items = list(items) if items else []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if self.is_empty():
            raise EmptyStackError("pop from an empty stack")
        return self._items.pop()

    def peek(self):
        if self.is_empty():
            raise EmptyStackError("peek at an empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Stack(bottom -> top: {self._items})"


class Queue:
    """FIFO queue backed by collections.deque (O(1) at both ends)."""

    def __init__(self, items=None):
        self._items = deque(items) if items else deque()

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        if self.is_empty():
            raise EmptyQueueError("dequeue from an empty queue")
        return self._items.popleft()

    def peek(self):
        if self.is_empty():
            raise EmptyQueueError("peek at an empty queue")
        return self._items[0]

    def is_empty(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Queue(front -> back: {list(self._items)})"


class ListQueue:
    """FIFO queue backed by a plain list; dequeue() is O(n)."""

    def __init__(self, items=None):
        self._items = list(items) if items else []

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        if self.is_empty():
            raise EmptyQueueError("dequeue from an empty queue")
        return self._items.pop(0)

    def peek(self):
        if self.is_empty():
            raise EmptyQueueError("peek at an empty queue")
        return self._items[0]

    def is_empty(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"ListQueue(front -> back: {self._items})"

