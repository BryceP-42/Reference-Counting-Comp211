#Reference Counting in CPython

##What it is: 

Reference Counting is the main garbage collection mechanism in CPython. Each object keeps a count of how many refernces point to it and when that count reaches 0, it is automatically deallocated.

"References" include:
    - a variable name
    - a slot inside any container (list, dict, other obj attributes)
    - a temporary reference while a function call is running
    - a global or statuc variable in a C function (for C)

##What it is used for:
    - automatically freeing memory
    - deciding when an object isn't needed, when it is inaccessible
    - 

##How it works
















# Reference Counting in Python (CPython)

A study summary covering what reference counting is, how it works, its
benefits and drawbacks, and how to observe it in code.

> **Scope:** Everything here describes **CPython**, the standard Python
> implementation. Other implementations may manage memory differently.

---

## 1. What it is

Reference counting is the main memory-management (garbage collection)
mechanism in CPython. Every object keeps an integer counting how many
references point to it. When that count reaches **zero**, the object is
deallocated immediately.

A "reference" can be:
- a variable name bound to the object
- a slot inside a container (list, dict, another object's attribute)
- a temporary reference held while a function call is running
- (in C code) a global/static variable or a local variable in a C function

## 2. What it is used for

- Automatically freeing memory so Python programmers don't call `free()`
  by hand.
- Deciding *when* an object is no longer needed: the moment nothing can
  reach it.
- Backed up by a separate **cyclic garbage collector** (the `gc` module)
  for the cases reference counting cannot handle (see section 4).

## 3. How it works

### What changes the count

| Action | Effect on count |
|---|---|
| `x = obj` (bind a name) | +1 |
| `y = x` (another name, **same** object, no copy) | +1 |
| `lst.append(obj)` / `[obj] * 5` | +1 per slot |
| Passing `obj` into a function | +1 while the function runs |
| `del x`, rebinding `x = something_else` | -1 |
| Container is cleared or itself freed | -1 per slot removed |
| Function returns (its parameters disappear) | -1 |

### The cascade

When an object's count hits zero it is freed, and the objects *it*
referenced each lose one reference. If any of those hit zero they are freed
too, and so on down the chain.

### Key idea: `del` removes a name, not an object

`del x` deletes the *name* `x`. The object is freed only if that was its
last reference. Printing `x` afterwards raises `NameError`, but that says
nothing about whether the object still exists in memory.

## 4. The weakness: reference cycles

```python
container = []
container.append(container)   # the list holds a reference to itself
del container                 # name gone, but the list still references itself
```

The list's count never reaches zero, so reference counting alone never
frees it. The object is unreachable by your program but still in memory
(a leak).

**The fix:** CPython adds a **cyclic garbage collector** that finds groups
of objects reachable only from each other and frees them.
- It lives in the `gc` module and only deals with *container* objects
  (objects that can hold references to other objects).
- It is generational: objects are grouped by how many collections they've
  survived. In older versions there are three generations. **Python 3.14
  has two (young and old)**, so check your version.
- Reference counting still runs normally even if the cyclic GC is disabled.

## 5. Benefits

- **Prompt cleanup:** objects are destroyed as soon as they become
  unreachable (except objects in cycles, which wait for the cyclic GC).
- **Fast in single-threaded code:** updating a counter is cheap.
- **Simple to understand and predict:** you can reason about exactly when
  an object dies.

## 6. Drawbacks

- **Cannot free cycles on its own**, so CPython needs a second mechanism.
- **Constant bookkeeping:** almost every new reference to an object is a
  *modification* (the count changes), even if you only read the object.
- **Not thread-safe by itself.** Two threads changing a count at the same
  time could corrupt it. CPython's **GIL** (global interpreter lock) makes
  this safe by letting only one thread run Python bytecode at a time, at
  the cost of no CPU parallelism across threads in a normal build.
  The experimental free-threaded build (PEP 703) replaces this with
  "biased" reference counting (separate local and shared counts).
- **Small memory cost:** every object carries a counter.

## 7. How to use / observe it

### Check a count: `sys.getrefcount`

```python
import sys

x = object()
print(sys.getrefcount(x))   # 2, not 1
```

The result is **always one higher than expected** because passing `x` into
the function creates a temporary reference. Subtract 1 for the real count.
(If you wrap this in your own helper function, that helper's parameter
adds another one, so subtract 2.)

### Watch an object die: `weakref`

A weak reference does **not** count toward keeping an object alive, so it
lets you observe whether an object still exists.

```python
import weakref

class Thing:
    pass

t = Thing()
w = weakref.ref(t)
print(w() is not None)   # True: object alive
del t
print(w() is not None)   # False: count hit zero, object freed
```

Notes:
- `list` and `dict` instances can't be weakly referenced directly; use a
  small class (or a subclass like `class MyList(list): pass`).
- `tuple` and `int` can't be weakly referenced at all in CPython, even
  when subclassed.

### Control the cyclic GC: the `gc` module

```python
import gc

gc.collect()    # run the cyclic collector now
gc.disable()    # turn off automatic cyclic collection
gc.enable()     # turn it back on
```

Use `gc.disable()` in experiments so automatic cleanup can't free your
cycle before you look at it.

## 8. Be ready to explain

1. Why `sys.getrefcount` shows one extra.
2. Why `b = a` doesn't copy a list, and what happens to the count of the
   list's *items* for `b = a`, `a.copy()`, and `copy.deepcopy(a)`.
3. Why `[t] * 5` adds 5 references to `t`.
4. Why `del x` followed by `print(x)` raises `NameError` while the object
   may still be in memory.
5. Why a self-referencing object is never freed by counts alone, and what
   frees it.
6. Why breaking one link in a ring of objects frees the whole ring
   immediately (the cascade), but leaving it intact does not.
7. Why the GIL exists in relation to reference counting.

## 9. Included examples (`refcount_examples/`)

| File | Demonstrates |
|---|---|
| `ex1_lists.py` | Lists hold one reference per slot (interactive) |
| `ex2_copies.py` | Alias vs `copy()` vs `deepcopy()` |
| `ex3_function.py` | Count inside vs outside a function |
| `ex4_ring.py` | Reference ring: leak vs cascade (interactive) |

Expected results (tested on Python 3.12.3): ex1 with inputs 5 and 2 gives
1, 6, 4, 1; ex2 gives 2, 2, 3, 3; ex3 gives 1, 2, 1; ex4 with 5 objects
leaves 0 alive if you break the ring first, or 5 alive until
`gc.collect()` if you don't.

## 10. Verification notes

**Checked against sources:** the definition and cascade behavior, cycles
and the cyclic collector, the 3.14 generation change, `gc.disable()`,
weak reference behavior and which types support them, and the GIL /
free-threading relationship.

**Not verified from sources (from memory; confirm before relying on it):**
since Python 3.12, some objects such as `None` and small integers are
"immortal" (PEP 683) and show very large reference counts, so don't use
them for counting demos. This is why the examples use a custom class.

**Version note:** exact counts and GC internals can differ between Python
versions.

## Sources

- Python docs, `gc` module: https://docs.python.org/3/library/gc.html
- Python docs, `weakref` module: https://docs.python.org/3/library/weakref
- CPython developer docs, "Garbage collector design" (`InternalDocs/garbage_collector.md` in the CPython repository)
- Python wiki, Global Interpreter Lock: https://wiki.python.org/moin/GlobalInterpreterLock.html
- PEP 703, Making the GIL Optional in CPython: https://peps.python.org/pep-0703/