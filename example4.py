# Example 1: lists hold references

## This code example lets you see how many references are stored in lists.
import sys


class Thing:
    pass


t = Thing()
print("Start (just the name t):", sys.getrefcount(t) - 1)

n = int(input("Put the same object in a list how many times? "))
items = [t] * n
print("After building the list:", sys.getrefcount(t) - 1)

k = int(input(f"Delete how many items from the front (0-{n})? "))
del items[:k]
print("After deleting:", sys.getrefcount(t) - 1)

items.clear()
print("After items.clear():", sys.getrefcount(t) - 1)