import pytest

import isort.literal
from isort import exceptions


def test_value_mismatch():
    with pytest.raises(exceptions.LiteralSortTypeMismatch):
        isort.literal.assignment("x = [1, 2, 3]", "set", "py")


def test_invalid_syntax():
    with pytest.raises(exceptions.LiteralParsingFailure):
        isort.literal.assignment("x = [1, 2, 3", "list", "py")


def test_invalid_sort_type():
    with pytest.raises(ValueError, match=r"Trying to sort using an undefined sort_type. Defined"):
        isort.literal.assignment("x = [1, 2, 3", "tuple-list-not-exist", "py")


def test_value_assignment_assignments():
    assert isort.literal.assignment("b = 1\na = 2\n", "assignments", "py") == "a = 2\nb = 1\n"


def test_assignments_invalid_section():
    with pytest.raises(exceptions.AssignmentsFormatMismatch):
        isort.literal.assignment("\n\nx = 1\nx++", "assignments", "py")


def test_value_last_basic():
    assert isort.literal.assignment("x = [3, 1, 2]", "value-last", "py") == "x = [1, 2, 3]"


def test_value_last_with_duplicates():
    assert isort.literal.assignment("x = [2, 1, 2, 3, 1]", "value-last", "py") == "x = [1, 2, 3]"


def test_value_last_with_strings():
    assert isort.literal.assignment("x = ['b', 'a', 'b', 'c']", "value-last", "py") == "x = ['a', 'b', 'c']"


def test_value_last_empty():
    assert isort.literal.assignment("x = []", "value-last", "py") == "x = []"
