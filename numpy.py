"""Minimal NumPy stub for environments without the real dependency."""

from __future__ import annotations

__all__ = [
    "array",
    "asarray",
    "ndarray",
    "float64",
    "bool_",
]


class ndarray(list):
    """Very small ndarray stand-in to satisfy type checks in tests."""

    def __array__(self) -> "ndarray":
        return self


float64 = float


class bool_(int):
    """Boolean scalar type used by pytest checks."""

    def __new__(cls, value):
        return int.__new__(cls, 1 if value else 0)


def array(iterable, dtype=None):  # noqa: D401
    """Return a list copy of the iterable (dtype ignored)."""
    return ndarray(iterable)


def asarray(iterable, dtype=None):
    return array(iterable, dtype=dtype)
