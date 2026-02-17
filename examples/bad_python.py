"""
An intentionally terrible Python file for testing BurnBook.
This code is designed to trigger as many rules as possible.
"""

# SECURITY: Hardcoded credentials (CMN003)
DB_PASSWORD = "supersecret123"
API_KEY = "sk-abc123def456ghi789jkl"
SECRET_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

# STYLE: Unused imports (PY008)
import os
import sys
import json
import re
import itertools
from collections import defaultdict  # unused

# STYLE: Wildcard import (PY007)
from os.path import *

# COMPLEXITY: Global mutable state (PY009)
GLOBAL_CACHE = {}
GLOBAL_LOCK = None

# SECURITY: Using eval (conceptual - would be caught in JS)


def f(a, b, c, d, e, f, g, h, i):
    """Single letter function name with way too many parameters."""
    # COMPLEXITY: Nested conditionals creating callback hell
    if a:
        if b:
            if c:
                if d:
                    if e:
                        for j in range(100):
                            while f:
                                try:
                                    if g and h and i:
                                        for k in range(10):
                                            if k % 2 == 0:
                                                pass
                                except:
                                    pass  # STYLE: Bare except (PY004)
    return None


# STYLE: Mutable default argument (PY005)
def add_item(item, items=[]):
    items.append(item)
    return items


# STYLE: Visually ambiguous names (PY003)
l = 1  # lowercase L
O = 0  # uppercase O
I = 1  # uppercase I


def process_data(data, callback, error_handler, finalizer):
    """
    A function that does too much and is too long.
    This is what happens when you don't refactor.
    """
    # First phase: validation
    if not data:
        print("No data provided")  # STYLE: Debug print (CMN006)
        return None

    # Second phase: transformation
    result = []
    for item in data:
        if item is not None:
            if isinstance(item, str):
                result.append(item.upper())
            elif isinstance(item, int):
                result.append(str(item))
            elif isinstance(item, dict):
                for key, value in item.items():
                    if key.startswith("_"):
                        continue
                    if callable(value):
                        try:
                            processed = value()
                            if processed:
                                result.append(processed)
                        except Exception:
                            pass
                    else:
                        result.append(f"{key}: {value}")

    # Third phase: callback chain (callback hell)
    if callback:
        callback(result, lambda x: error_handler(x) if x else None)

    # Fourth phase: finalization
    if finalizer:
        finalizer(result)

    # Fifth phase: logging
    print(f"Processed {len(result)} items")  # STYLE: Debug print (CMN006)

    return result


# TODO: Implement actual business logic here (CMN002)
# FIXME: This is broken on weekends (CMN002)
# HACK: Don't touch this, it works somehow (CMN002)
# XXX: Temporary solution (CMN002)


def x(l, O, I):  # STYLE: Single letter function with ambiguous params
    """bad naming"""
    pass


class BigClass:
    """A class with too many methods."""

    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
    def method13(self): pass
    def method14(self): pass
    def method15(self): pass
    def method16(self): pass
    def method17(self): pass
    def method18(self): pass
    def method19(self): pass
    def method20(self): pass
    def method21(self): pass
    def method22(self): pass
    def method23(self): pass
    def method24(self): pass
    def method25(self): pass


# STYLE: Very long line (CMN001)
very_long_variable_name_that_goes_on_forever_and_ever_and_ever_and_ever_and_ever_and_ever_and_ever_and_ever_and_ever_and_ever_and_ever = 42


if __name__ == "__main__":
    print("Starting program...")
    result = f(1, 2, 3, 4, 5, True, True, True, True)
    print(f"Result: {result}")
