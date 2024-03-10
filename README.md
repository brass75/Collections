### Collections Package

This is a package of some basic (and not so basic) collections I wanted to write my
own implementations of. The goal is not to replicate or deprecate the `collections` 
module in Python but to have something that has things I need or want. 

### Current Collections

## Dictionary

A personal implementation of a `dict` object. Ideally will have all the functionality
of the standard `dict` with the simple difference that looping over it gives the 
`key`, `value` pair instead of just the `key`.

### Expected Collections

## DefaultDict

Extension of the Dictionary Class to allow it to take an additional parameter of a 
factory to use to create a default value if a key is not present.

## AttrDict

Extension of the dictionary class that will allow `.` access to variables.

## HashableDict

This will be an _immutable_ dictionary class - once initialized it cannot be modified.
This will allow the use of dictionaries as data sources in memoized functions and methods.

### Contributing

Feel free to fork and create a PR to add any additional collections you would like. 
If you want to add a new collection please make sure to update this README.md with
information on the collection(s) you add.

As I get farther along in this process I will add testing and packaging, but I'm not 
that far along yet.
