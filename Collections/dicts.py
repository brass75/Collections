"""
Assorted dictionary types

:copyright: (c) 2024 by Dan Shernicoff
"""
from collections.abc import Iterable
from typing import Sized, Any


class Dictionary:
    """
    Basic Dictionary class.
    """
    def __init__(self, kv_pairs: Iterable = None, max_len: int = 4):
        self.len = 0
        self.max_len = max_len
        self.multiplier = 2
        self.store = [(None, None) for _ in range(self.max_len)]
        self.iterators = -1
        if kv_pairs:
            if isinstance(kv_pairs, dict):
                for key, value in kv_pairs.items():
                    self[key] = value
            else:
                for key, value in kv_pairs:
                    self[key] = value

    def __setitem__(self, key, value):
        """ Add item to the dictionary """
        if key is None:
            raise ValueError('Key cannot be None')
        if self.len >= self.max_len:
            new_dict = self.__class__(self._get_values(), max_len=self.max_len*self.multiplier)
            self.len = new_dict.len
            self.max_len = new_dict.max_len
            self.store = new_dict.store
        key_hash = hash(key) % self.max_len
        if self.store[key_hash][0] == key or self.store[key_hash][0] is None:
            self.store[key_hash] = (key, value)
        else:
            new_dict = self.__class__(self._get_values(), max_len=self.max_len*self.multiplier)
            self.len = new_dict.len
            self.max_len = new_dict.max_len
            self.store = new_dict.store
            self[key] = value

    def __getitem__(self, key):
        """ Get item from the dictionary """
        key_hash = hash(key) % self.max_len
        if self.store[key_hash][0] == key:
            return self.store[key_hash][1]
        raise KeyError(f'{key} not found in {self.__class__.__name__}')

    def __delitem__(self, key):
        """ Delete item from the dictionary """
        key_hash = hash(key) % self.max_len
        if self.store[key_hash][0] == key:
            self.store[key_hash] = (None, None)
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
            if self.store[self.iterators][0] is not None:
                self.iterators += 1
                return self.store[self.iterators -1]
            self.iterators += 1
        self.iterators = -1
        raise StopIteration

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
        return self.store[key_hash][0] == key

    def as_dict(self):
        return dict(self._get_values())

    def _get_values(self) -> list[tuple[Any, Any]]:
        """ Get values from the dictionary """
        return [(k, v) for k, v in self.store if k is not None]

    def values(self) -> list[Any]:
        """ Get values from the dictionary """
        return [v for _, v in self._get_values()]

    def items(self) -> list[tuple[Any, Any]]:
        """ Get items from the dictionary """
        return self._get_values()

    def keys(self) -> list[Any]:
        """ Get keys from the dictionary """
        return [k for k, _ in self._get_values()]

    def get(self, key: Any, default=None) -> Any:
        """ Get a value from the dictionary """
        try:
            return self[key]
        except KeyError:
            return default


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
    print('Done')
