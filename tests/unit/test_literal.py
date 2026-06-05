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


def test_unique_dict():
    # Regular dict sorts by value but doesn't deduplicate by value (dict keys are inherently unique)
    # unique-dict should deduplicate by value and keep the last corresponding key-value pair
    assert isort.literal.assignment('y = {"a": "c", "b": "c", "c": "z"}', "unique-dict", "py") == "y = {'b': 'c', 'c': 'z'}"
    assert isort.literal.assignment('y = {"a": 2, "b": 1, "c": 2}', "unique-dict", "py") == "y = {'b': 1, 'c': 2}"
    assert isort.literal.assignment('y = {"z": 3, "a": 1, "b": 1, "c": 2, "d": 2}', "unique-dict", "py") == "y = {'b': 1, 'd': 2, 'z': 3}"
