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


def test_value_assignment_dict():
    assert (
        isort.literal.assignment("x = {'b': 2, 'a': 1}", "dict", "py")
        == "x = {'a': 1, 'b': 2}"
    )


def test_value_assignment_unique_dict():
    assert (
        isort.literal.assignment("x = {'a': 3, 'b': 1, 'c': 2, 'd': 1}", "unique-dict", "py")
        == "x = {'d': 1, 'c': 2, 'a': 3}"
    )


def test_value_assignment_unique_dict_empty():
    assert (
        isort.literal.assignment("x = {}", "unique-dict", "py")
        == "x = {}"
    )


def test_value_assignment_unique_dict_single():
    assert (
        isort.literal.assignment("x = {'a': 1}", "unique-dict", "py")
        == "x = {'a': 1}"
    )


def test_value_assignment_unique_dict_all_unique():
    assert (
        isort.literal.assignment("x = {'b': 2, 'a': 1, 'c': 3}", "unique-dict", "py")
        == "x = {'a': 1, 'b': 2, 'c': 3}"
    )


def test_value_assignment_unique_dict_duplicate_values():
    assert (
        isort.literal.assignment("x = {'a': 1, 'b': 1, 'c': 1}", "unique-dict", "py")
        == "x = {'c': 1}"
    )


def test_value_mismatch_unique_dict():
    with pytest.raises(exceptions.LiteralSortTypeMismatch):
        isort.literal.assignment("x = [1, 2, 3]", "unique-dict", "py")
