import pytest

import isort
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


def test_existing_literal_sort_types():
    assert isort.literal.assignment("x = {'b': 2, 'a': 1}\n", "dict", "py") == "x = {'a': 1, 'b': 2}\n"
    assert isort.literal.assignment("x = ['b', 'a']\n", "list", "py") == "x = ['a', 'b']\n"
    assert isort.literal.assignment("x = ['b', 'a', 'a']\n", "unique-list", "py") == "x = ['a', 'b']\n"


def test_unique_value_dict_assignment():
    once = isort.literal.assignment(
        "x = {'b': 1, 'a': 1, 'c': 2}\n", "unique-value-dict", "py"
    )

    assert once == "x = {'a': 1, 'c': 2}\n"
    assert isort.literal.assignment(once, "unique-value-dict", "py") == once


def test_unique_value_dict_code_sort_comment():
    assert isort.code("# isort: unique-value-dict\nx = {'b': 1, 'a': 1, 'c': 2}\n") == (
        "# isort: unique-value-dict\nx = {'a': 1, 'c': 2}\n"
    )


def test_assignments_invalid_section():
    with pytest.raises(exceptions.AssignmentsFormatMismatch):
        isort.literal.assignment("\n\nx = 1\nx++", "assignments", "py")
