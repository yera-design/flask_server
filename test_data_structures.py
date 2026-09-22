import unittest

from data_structures import EmptyQueueError, EmptyStackError, ListQueue, Queue, Stack


class TestStack(unittest.TestCase):
    def setUp(self):
        self.stack = Stack()

    def test_new_stack_is_empty(self):
        self.assertTrue(self.stack.is_empty())
        self.assertEqual(len(self.stack), 0)

    def test_push_increases_length(self):
        self.stack.push(1)
        self.assertEqual(len(self.stack), 1)
        self.stack.push(2)
        self.assertEqual(len(self.stack), 2)

    def test_pop_returns_most_recently_pushed_item(self):
        self.stack.push("a")
        self.stack.push("b")
        self.stack.push("c")
        self.assertEqual(self.stack.pop(), "c")
        self.assertEqual(self.stack.pop(), "b")
        self.assertEqual(self.stack.pop(), "a")

    def test_pop_decreases_length_and_empties_stack(self):
        self.stack.push(1)
        self.stack.push(2)
        self.stack.pop()
        self.assertEqual(len(self.stack), 1)
        self.stack.pop()
        self.assertTrue(self.stack.is_empty())

    def test_pop_on_empty_stack_raises(self):
        with self.assertRaises(EmptyStackError):
            self.stack.pop()

    def test_peek_returns_top_without_removing_it(self):
        self.stack.push(10)
        self.stack.push(20)
        self.assertEqual(self.stack.peek(), 20)
        self.assertEqual(len(self.stack), 2)

    def test_peek_on_empty_stack_raises(self):
        with self.assertRaises(EmptyStackError):
            self.stack.peek()

    def test_initializing_with_items(self):
        stack = Stack(items=[1, 2, 3])
        self.assertEqual(len(stack), 3)
        self.assertEqual(stack.pop(), 3)


class QueueContractTests:
    QUEUE_CLASS = None

    def setUp(self):
        self.queue = self.QUEUE_CLASS()

    def test_new_queue_is_empty(self):
        self.assertTrue(self.queue.is_empty())
        self.assertEqual(len(self.queue), 0)

    def test_enqueue_increases_length(self):
        self.queue.enqueue(1)
        self.assertEqual(len(self.queue), 1)
        self.queue.enqueue(2)
        self.assertEqual(len(self.queue), 2)

    def test_dequeue_returns_items_in_the_order_they_were_added(self):
        self.queue.enqueue("a")
        self.queue.enqueue("b")
        self.queue.enqueue("c")
        self.assertEqual(self.queue.dequeue(), "a")
        self.assertEqual(self.queue.dequeue(), "b")
        self.assertEqual(self.queue.dequeue(), "c")

    def test_dequeue_decreases_length_and_empties_queue(self):
        self.queue.enqueue(1)
        self.queue.enqueue(2)
        self.queue.dequeue()
        self.assertEqual(len(self.queue), 1)
        self.queue.dequeue()
        self.assertTrue(self.queue.is_empty())

    def test_dequeue_on_empty_queue_raises(self):
        with self.assertRaises(EmptyQueueError):
            self.queue.dequeue()

    def test_peek_returns_front_without_removing_it(self):
        self.queue.enqueue(10)
        self.queue.enqueue(20)
        self.assertEqual(self.queue.peek(), 10)
        self.assertEqual(len(self.queue), 2)

    def test_peek_on_empty_queue_raises(self):
        with self.assertRaises(EmptyQueueError):
            self.queue.peek()

    def test_initializing_with_items(self):
        queue = self.QUEUE_CLASS(items=[1, 2, 3])
        self.assertEqual(len(queue), 3)
        self.assertEqual(queue.dequeue(), 1)


class TestQueue(QueueContractTests, unittest.TestCase):
    QUEUE_CLASS = Queue


class TestListQueue(QueueContractTests, unittest.TestCase):
    QUEUE_CLASS = ListQueue


if __name__ == "__main__":
    unittest.main()

