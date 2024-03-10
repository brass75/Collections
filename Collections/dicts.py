"""
Assorted dictionary types

:copyright: (c) 2024 by Dan Shernicoff
"""
import copy
from collections.abc import Iterable, Callable
from typing import Sized, Any


class Dictionary:
    """
    Basic Dictionary class.
    """
    def __init__(self, kv_pairs: Iterable = None, max_len: int = 4):
        self.len = 0
        self.max_len = max_len
        self.multiplier = 2
        self.store: list = [None for _ in range(self.max_len)]
        self.iterators = -1
        self.added = 0
        if kv_pairs:
            if isinstance(kv_pairs, dict):
                for key, value in kv_pairs.items():
                    self[key] = value
            else:
                for key, value in kv_pairs:
                    self[key] = value

    def __setitem__(self, key, value):
        """ Add item to the dictionary """
        if self.len >= self.max_len:
            new_dict = self.__class__(self._get_values(), max_len=self.max_len*self.multiplier)
            self.len = new_dict.len
            self.max_len = new_dict.max_len
            self.store = new_dict.store
        key_hash = hash(key) % self.max_len
        if not self.store[key_hash] or (self.store[key_hash] and self.store[key_hash][0]) == key:
            if not self.store[key_hash]:
                self.len += 1
            self.store[key_hash] = (key, value, self.added)
            self.added += 1
        else:
            new_dict = self.__class__(self._get_values(), max_len=self.max_len*self.multiplier)
            self.len = new_dict.len
            self.max_len = new_dict.max_len
            self.store = new_dict.store
            self[key] = value

    def __getitem__(self, key):
        """ Get item from the dictionary """
        key_hash = hash(key) % self.max_len
        if self.store[key_hash] and self.store[key_hash][0] == key:
            return self.store[key_hash][1]
        raise KeyError(f'{key} not found in {self.__class__.__name__}')

    def __delitem__(self, key):
        """ Delete item from the dictionary """
        key_hash = hash(key) % self.max_len
        if self.store[key_hash] and self.store[key_hash][0] == key:
            self.store[key_hash] = None
            self.len -= 1
            return
        raise KeyError(f'{key} not found in {self.__class__.__name__}')

    def __iter__(self):
        """ Iterate over the dictionary """
        self.iterators = 0
        return self

    def __next__(self):
        """ Get next item from the dictionary """
        if self.iterators > self.max_len or self.iterators < 0:
            self.iterators = -1
            raise StopIteration
        while self.iterators < self.max_len:
            if self.store[self.iterators]:
                self.iterators += 1
                return self.store[self.iterators -1][0], self.store[self.iterators -1][1]
            self.iterators += 1
        self.iterators = -1
        raise StopIteration

    def __len__(self):
        """ Size of the dictionary """
        return self.len

    def __repr__(self):
        """ Print out the dictionary as a representation """
        return f'Dictionary({self._get_values()}, max_len={self.max_len})'

    def __str__(self):
        """ Print out the dictionary """
        s = '{\n'
        s += ',\n'.join(f'{k!r}: {v!r}' for k, v in self._get_values())
        s += '\n}'
        return s

    def __contains__(self, key):
        """ Check if a key is in the dictionary """
        key_hash = hash(key) % self.max_len
        return self.store[key_hash] and self.store[key_hash][0] == key

    def __eq__(self, other):
        """ Check if two dictionaries are equal """
        return self.items() == other.items()

    def as_dict(self) -> dict:
        return dict(self._get_values())

    def _get_values(self) -> list[tuple[Any, Any]]:
        """ Get values from the dictionary """
        return [(k, v) for k, v, *_ in sorted((kv for kv in self.store if kv), key=lambda item: item[2])]

    def values(self) -> list[Any]:
        """ Get values from the dictionary """
        return [v for _, v, *_ in self._get_values()]

    def items(self) -> list[tuple[Any, Any]]:
        """ Get items from the dictionary """
        return self._get_values()

    def keys(self) -> list[Any]:
        """ Get keys from the dictionary """
        return [k for k, *_ in self._get_values()]

    def get(self, key: Any, default=None) -> Any:
        """ Get a value from the dictionary """
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key: Any, default=None) -> Any:
        """ Pop a value from the dictionary """
        if key in self:
            rc = self[key]
            del self[key]
            return rc
        if default is not None:
            return default
        raise KeyError(f'{key!r} not found in dictionary')

    def popitem(self) -> tuple[Any, Any]:
        """ Pop a value from the dictionary """
        if keys := self.keys():
            return keys[-1], self.pop(keys[-1])
        raise KeyError('Attempt to pop from empty dictionary.')

    def update(self, items: Iterable[tuple[Any, Any]]|dict) -> None:
        """ Update the dictionary with values from items """
        if isinstance(items, dict):
            for k, v in items.items():
                self[k] = v
        else:
            for k, v in items:
                self[k] = v

    def setdefault(self, key: Any, default: Callable) -> Any:
        """ Retrieve the value for key from the dictionary. If it does not exist, add it with a value of default """
        if key not in self:
            self[key] = default()
        return self[key]

    @classmethod
    def fromkeys(cls, keys: Iterable[Any], value: Any = None):
        """ Create a new dictionary from a set of keys with optional default value """
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

    d.update((n, n+1) for n in range(50, 70, 2))

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
    print('Done')
