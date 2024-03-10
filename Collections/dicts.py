"""
Assorted dictionary types

:copyright: (c) 2024 by Dan Shernicoff
"""
import copy
from collections.abc import Iterable, Callable, Hashable
from typing import Sized, Any


class Dictionary:
    """
    Basic Dictionary class.
    """
    _MAX_LEN = 4
    _MULTIPLIER = 2
    _SENTINEL = object()

    def __init__(self, kv_pairs: Iterable = None, /, max_len: int = _MAX_LEN,
                 multiplier: int = _MULTIPLIER):
        """
        Create a new, ordered, dictionary.

        :param kv_pairs: Optional set of key, value pairs to add to the dictionary. Can be a dict or any other iterable
                         containing 2 or more values per entry. (NOTE: If there are more than 2 values per entry the
                         first 2 will be used and the rest ignored.)
        :param max_len: Optional maximum length of the storage. Default is 4.
        :param multiplier: Optional multiplier for the storage. Default is 2.
        """
        self._len = 0
        self._max_len = max_len
        self._multiplier = multiplier
        self._store: list = [None for _ in range(self._max_len)]
        self._iterators = -1
        self._added = 0
        if kv_pairs:
            if isinstance(kv_pairs, dict):
                for key, value in kv_pairs.items():
                    self[key] = value
            else:
                for key, value, *_ in kv_pairs:
                    self[key] = value

    def __setitem__(self, key: Hashable, value: Any):
        """
        Add/Update item to the dictionary at key

        :param key: Key to add/update
        :param value: Value to set
        """
        if self._len >= self._max_len:
            new_dict = self.__class__(self.items(), max_len=self._max_len * self._multiplier)
            self._len = new_dict._len
            self._max_len = new_dict._max_len
            self._store = new_dict._store
        try:
            key_hash = hash(key) % self._max_len
        except TypeError as e:
            raise e from None
        if not self._store[key_hash] or (self._store[key_hash] and self._store[key_hash][0]) == key:
            if not self._store[key_hash]:
                self._len += 1
            self._store[key_hash] = (key, value, self._added)
            self._added += 1
        else:
            new_dict = self.__class__(self.items(), max_len=self._max_len * self._multiplier)
            self._len = new_dict._len
            self._max_len = new_dict._max_len
            self._store = new_dict._store
            self[key] = value

    def __getitem__(self, key: Hashable) -> Any:
        """
        Get item from the dictionary

        :param key: key to retrieve
        :return: the value at key
        :raises: KeyError if key is not found
        """
        try:
            key_hash = hash(key) % self._max_len
            if self._store[key_hash] and self._store[key_hash][0] == key:
                return self._store[key_hash][1]
        except TypeError:
            # This should be treated as a KeyError even though the root cause is that we can't hash the provided key.
            ...
        raise KeyError(f'{key} not found in {self.__class__.__name__}')

    def __delitem__(self, key: Hashable) -> None:
        """
        Delete item from the dictionary

        :param key: key to retrieve
        :raises: KeyError if key is not found
        """
        try:
            key_hash = hash(key) % self._max_len
            if self._store[key_hash] and self._store[key_hash][0] == key:
                self._store[key_hash] = None
                self._len -= 1
                return
        except TypeError:
            # This should be treated as a KeyError even though the root cause is that we can't hash the provided key.
            ...
        raise KeyError(f'{key} not found in {self.__class__.__name__}')

    def __iter__(self):
        """ Iterate over the dictionary """
        self._iterators = 0
        return self

    def __next__(self):
        """ Get next item from the dictionary """
        if self._iterators > self._max_len or self._iterators < 0:
            self._iterators = -1
            raise StopIteration
        while self._iterators < self._max_len:
            if self._store[self._iterators]:
                self._iterators += 1
                return self._store[self._iterators - 1][0], self._store[self._iterators - 1][1]
            self._iterators += 1
        self._iterators = -1
        raise StopIteration

    def __len__(self):
        """ Length of the dictionary """
        return self._len

    def __repr__(self):
        """ Print out the dictionary as a representation """
        return f'Dictionary({self.items()}, max_len={self._max_len}, multiplier={self._multiplier})'

    def __str__(self):
        """ Return a formatted, string representation of the dictionary """
        s = '{\n'
        s += ',\n'.join(f'{k!r}: {v!r}' for k, v in self.items())
        s += '\n}'
        return s

    def __contains__(self, key: Any) -> bool:
        """
        Check if a key is in the dictionary

        :param key: The key to check if it is in the dictionary
        NOTE: If the key is not hashable (and therefore cannot be a key in the dictionary, False will be returned
        rather than an exception raised.)
        """
        try:
            key_hash = hash(key) % self._max_len
        except TypeError:
            return False
        return self._store[key_hash] and self._store[key_hash][0] == key

    def __eq__(self, other):
        """ Check if two dictionaries are equal """
        return self.items() == other.items()

    def __hash__(self):
        """ Raise a TypeError as this is not Hashable. """
        raise TypeError(f'Unhashable type {self.__class__.__name__}')

    def as_dict(self) -> dict:
        """ Convert the dictionary into a standard, Python, dict object """
        return dict(self.items())

    def items(self) -> list[tuple[Any, Any]]:
        """ Get key-value pairs from the dictionary """
        return [(k, v) for k, v, *_ in sorted((kv for kv in self._store if kv), key=lambda item: item[2])]

    def values(self) -> list[Any]:
        """ Get values from the dictionary """
        return [v for _, v, *_ in self.items()]

    def keys(self) -> list[Hashable]:
        """ Get keys from the dictionary """
        return [k for k, *_ in self.items()]

    def get(self, key: Hashable, default=None) -> Any:
        """
        Get a value from the dictionary

        :param key: The key to retrieve the value for
        :param default: The default value to return if the key is not present in the dictionary
        :return: The value at key or default
        """
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key: Hashable, default=_SENTINEL) -> Any:
        """
        Pop the value at key from the dictionary

        :param key: The key to pop
        :param default: The default value to return if the key is not set
        :return: The value at key or default if default is set
        :raises: KeyError if key is not found and default is not set
        """
        if key in self:
            rc = self[key]
            del self[key]
            return rc
        if default is not self._SENTINEL:
            return default
        raise KeyError(f'{key!r} not found in dictionary')

    def popitem(self) -> tuple[Hashable, Any]:
        """ Pop the most recently added key-value pair from the dictionary """
        if keys := self.keys():
            return keys[-1], self.pop(keys[-1])
        raise KeyError('Attempt to pop from empty dictionary.')

    def update(self, items: Iterable[tuple[Any, Any]] | dict) -> None:
        """ Update the dictionary with values from items """
        if isinstance(items, dict):
            for k, v in items.items():
                self[k] = v
        else:
            for k, v in items:
                self[k] = v

    def setdefault(self, key: Hashable, default: Callable, *args, **kwargs) -> Any:
        """
         Retrieve the value for key from the dictionary. If it does not exist, add it with a value of default

         :param key: the key
         :param default: the default value to set key to if it does not exist. Must be a factory.
         :param args: positional arguments to pass to the factory
         :param kwargs: named arguments to pass to the factory
         :return: the value at key or the result of calling default with **kwargs
         """
        if key not in self:
            self[key] = default(*args, **kwargs)
        return self[key]

    @classmethod
    def fromkeys(cls, keys: Iterable[Hashable], value: Any = None):
        """
        Create a new dictionary from a set of keys with optional default value

        :param keys: the keys to seed the new dictionary with
        :param value: the default value to use for all keys
        :return: A new dictionary
        """
        return cls((k, value) for k in keys)


if __name__ == '__main__':
    d = Dictionary([(f'{n}', f'{n}') for n in range(5)])
    print(d)
    print(repr(d))
    print(d.as_dict())
    print()

    for k, v in d:
        print(f'{k}: {v}')

    for n in range(10):
        d[str(n)] = str(n ** 2)

    print(d)
    print()

    print(f'{'1' in d=}')
    print(f'{'100' in d=}')
    print()

    print(d.get('5'))
    print(d.get('100'))
    print()

    d.update((n, n + 1) for n in range(50, 70, 2))

    print(d)
    print()

    d.update({n: n + 1 for n in range(20, 40, 2)})
    print(d)

    print()

    print(len(d))
    print(d.popitem())
    print(d.pop(20))
    print(d)
    print(len(d))

    new_d = Dictionary()
    new_d.setdefault('l', list).extend([10, 20, 30])
    print(new_d)

    new_d = Dictionary.fromkeys(range(5), 0)
    print(new_d)

    new_d = Dictionary.fromkeys(range(5))
    print(new_d)

    another_d = copy.copy(new_d)
    assert another_d == new_d
    assert new_d != d
    print(new_d.pop('a', None))
    try:
        print(new_d.pop('b'))
    except KeyError as e:
        print(f'Got {e=}')
    print('Done')
