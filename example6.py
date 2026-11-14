# Example 3: passing an object to a function

## reference count increases when inside a function and decreases after a return.
import sys


class Thing:
    pass


def inspect(obj):
    print("Inside the function: ", sys.getrefcount(obj) - 1)


t = Thing()
print("Outside the function:", sys.getrefcount(t) - 1)
inspect(t)
print("After it returns:    ", sys.getrefcount(t) - 1)