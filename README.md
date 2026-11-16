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











