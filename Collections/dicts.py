"""
Assorted dictionary types

:copyright: (c) 2024 by Dan Shernicoff
"""
from collections.abc import Iterable, Callable
from typing import Any


class Dictionary:
    """
    Basic Dictionary class.
    """
    START_LEN = 4
    MULTIPLIER = 2

    def __init__(self, kv_pairs: Iterable = None, max_len: int = START_LEN, multiplier: int = MULTIPLIER):
        self.len = 0
        self.max_len = max_len
        self.multiplier = multiplier
        self.store = [(None, None) for _ in range(self.max_len)]
        self.iterators = -1
        self._kwargs_ = {}
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
            new_dict = self.__class__(kv_pairs=self._get_values(), max_len=self.max_len*self.multiplier,
                                      **self._kwargs_)
            self.len = new_dict.len
            self.max_len = new_dict.max_len
            self.store = new_dict.store
        key_hash = hash(key) % self.max_len
        if self.store[key_hash][0] == key or self.store[key_hash][0] is None:
            self.store[key_hash] = (key, value)
            self.len += 1
        else:
            new_dict = self.__class__(kv_pairs=self._get_values(), max_len=self.max_len*self.multiplier,
                                      **self._kwargs_)
            self.len = new_dict.len
            self.max_len = new_dict.max_len
            self.store = new_dict.store
            self[key] = value

    def __getitem__(self, key):
        """ Get item from the dictionary """
        key_hash = hash(key) % self.max_len
        if self.store[key_hash][0] == key:
            return self.store[key_hash][1]
        if hasattr(self, '__missing__'):
            return self.__missing__(key)
        raise KeyError(f'{key} not found in {self.__class__.__name__}')

    def __delitem__(self, key):
        """ Delete item from the dictionary """
        key_hash = hash(key) % self.max_len
        if self.store[key_hash][0] != key:
            raise KeyError(f'{key} not found in {self.__class__.__name__}')
        self.store[key_hash] = (None, None)
        self.len -= 1

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
        return f'{self.__class__.__name__}({self._get_values()}, max_len={self.max_len})'

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

    def __len__(self):
        """ Return the length of the dictionary """
        return self.len

    def clear(self):
        """ Clear the dictionary """
        self.max_len = self.START_LEN
        self.store = [(None, None) for _ in range(self.multiplier)]
        self.len = 0
        self.iterators = -1

    def copy(self):
        return self.__class__(self)

    @staticmethod
    def fromkeys(keys: Iterable[Any], value: Any = None):
        """ Create a new dictionary from a set of keys """
        return Dictionary(((k, value) for k in keys))

    def pop(self, key: Any, default: Any = None) -> Any:
        """ Remove and return the value from the dictionary """
        key_hash = hash(key) % self.max_len
        if self.store[key_hash][0] == key:
            value = self.store[key_hash][1]
            self.store[key_hash] = (None, None)
            return value
        if default is not None:
            return default
        raise KeyError(f'{key!r} not in dictionary')

    def as_dict(self):
        return dict(self._get_values())

    def _get_values(self) -> list[tuple[Any, Any]]:
        """ Get values from the dictionary """
        return [(k, v) for k, v in self.store if k is not None]

    def setdefault(self, key: Any, default: Any = None) -> Any:
        """ Set values from the dictionary """
        if key not in self:
            self[key] = default
        return self[key]

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


class DefaultDict(Dictionary):
    """ Default dictionary"""
    def __init__(self, factory: Callable = None, *args, **kwargs):
        """ Initialize the class """
        if not factory or not isinstance(factory, Callable):
            raise ValueError('factory must be a callable')
        super().__init__(*args, **kwargs)
        self._kwargs_['factory'] = self._factory_ = factory

    def __missing__(self, key: Any) -> Any:
        """ Handle missing key """
        self[key] = self._factory_()
        return self[key]


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
    del(d['5'])
    print(d.get('5'))

    print()

    dd = DefaultDict(lambda: 'New entry')
    print(dd['a'])
    print(dd['b'])
    dd['c'] += ' added to'
    for k, v in dd:
        print(f'{k}: {v}')

    print('Done')
