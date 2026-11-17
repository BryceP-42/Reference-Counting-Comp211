# Reference Counting in CPython

## What it is: 

Reference Counting is the main garbage collection mechanism in CPython. Each object keeps a count of how many refernces point to it and when that count reaches 0, it is automatically deallocated.

"References" include:
    - a variable name
    - a slot inside any container (list, dict, other obj attributes)
    - a temporary reference while a function call is running
    - a global or statuc variable in a C function (for C)

## What it is used for:
    - automatically freeing memory
    - deciding when an object isn't needed, when it is inaccessible
    - 

## How it works:

What changes the count

Action                                 |       Effect on count
------------------------------------------------------------------------
x = obj name                           |    +1
y = x                                  |    +1
lst.append(obj)/[obj]*5                |    +1 per slot
Passing obj into a function            |    +1 while the function runs
del x, rebinding x = something_else    |    -1
Container is clearned or itself freed  |    -1 per slot removed
Function returns                       |    -1

Note: When an objects count reaches 0, it is freed, and the objects it referenced each lose one reference, and if any of those his 0 they are freed too.

## Drawbacks

ex:
```python
container = []
container.append(container)   # the list holds a reference to itself#
del container                 # the name is gone, but the list still references itself
```


The object becomes unreachable because the list's count never reaches 0, but the reference to it that isn't itself is gone.

Cyclic garbage collector: 

CPython has a cyclic garbage collector that finds objects that are only reachable from each other, and frees them.
    - lives in the gc module and only deals with container objects.

## Benefits

    - **Prompt cleanup:** objects are destroyed as soon as they become unreachable.
    - **Simple to understand and predict:** it is simple enough to reason when an object dies.
    - **Fast code:** updating a counter is cheap.

## Drawbacks

    - Cannot free cycles on its own: needs a second mechanism
    - Contant bookkeeping: keeping track of every counter.
    - Not thread-safe by itself: 
    - Small memory cost: every object carries a counter, could add up.

## How to use:

    - Check a count: sys.getrefcount(x)
        - This result is one higher than expected because passing x creates a temporary reference.
    - weakref?
    - control the cyclic gc:
        - gc.collect()  runs the cyclic collector now
        - gc.disable()  turns off automatic cyclic collection
        - gc.enable()   turns it on
    