import unittest

from stack_queue_algorithms import (
    generate_binary_numbers,
    is_balanced,
    is_palindrome,
    reverse_string,
)


class TestIsBalanced(unittest.TestCase):
    def test_simple_matched_pairs(self):
        self.assertTrue(is_balanced("()"))
        self.assertTrue(is_balanced("[]"))
        self.assertTrue(is_balanced("{}"))

    def test_nested_and_mixed_brackets(self):
        self.assertTrue(is_balanced("([{}])"))
        self.assertTrue(is_balanced("(a + [b * (c - d)]) / {e}"))

    def test_empty_string_is_balanced(self):
        self.assertTrue(is_balanced(""))

    def test_text_with_no_brackets_is_balanced(self):
        self.assertTrue(is_balanced("hello world"))

    def test_unmatched_opening_bracket(self):
        self.assertFalse(is_balanced("(("))

    def test_unmatched_closing_bracket(self):
        self.assertFalse(is_balanced("))"))

    def test_wrong_order(self):
        self.assertFalse(is_balanced(")("))

    def test_mismatched_bracket_types(self):
        self.assertFalse(is_balanced("[a + (b)}"))


class TestReverseString(unittest.TestCase):
    def test_normal_word(self):
        self.assertEqual(reverse_string("hello"), "olleh")

    def test_empty_string(self):
        self.assertEqual(reverse_string(""), "")

    def test_single_character(self):
        self.assertEqual(reverse_string("x"), "x")

    def test_sentence_with_spaces(self):
        self.assertEqual(reverse_string("ab c"), "c ba")


class TestIsPalindrome(unittest.TestCase):
    def test_palindromes(self):
        self.assertTrue(is_palindrome("racecar"))
        self.assertTrue(is_palindrome("noon"))

    def test_non_palindromes(self):
        self.assertFalse(is_palindrome("hello"))
        self.assertFalse(is_palindrome("abc"))

    def test_empty_string_is_a_palindrome(self):
        self.assertTrue(is_palindrome(""))

    def test_single_character_is_a_palindrome(self):
        self.assertTrue(is_palindrome("z"))

    def test_case_sensitive_by_design(self):
        self.assertFalse(is_palindrome("Noon"))


class TestGenerateBinaryNumbers(unittest.TestCase):
    def test_n_equals_zero_returns_empty_list(self):
        self.assertEqual(generate_binary_numbers(0), [])

    def test_negative_n_returns_empty_list(self):
        self.assertEqual(generate_binary_numbers(-3), [])

    def test_n_equals_one(self):
        self.assertEqual(generate_binary_numbers(1), ["1"])

    def test_first_five_binary_numbers(self):
        self.assertEqual(
            generate_binary_numbers(5), ["1", "10", "11", "100", "101"]
        )

    def test_output_length_matches_n(self):
        self.assertEqual(len(generate_binary_numbers(20)), 20)


if __name__ == "__main__":
    unittest.main()

