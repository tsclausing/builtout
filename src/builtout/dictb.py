import collections


class dictb(dict):
    """
    A dict implementation with enhanced functionality, preserving most expected builtin behavior.
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._viewkeys = self.viewkeys()

    # subscript

    def __getitem__(self, key):
        """
        Hashable item -> value

            >>> dictb(a=1, b=2, c=3)['b']
            2

        Sequence item -> value generator

            >>> tuple( dictb(a=1, b=2, c=3)[['a', 'c']] )
            (1, 3)

        Set item -> dictb for keys in Set

            >>> dictb(a=1, b=2, c=3)[{'a', 'c'}] == dictb(a=1, c=3)
            True
        """
        if isinstance(key, collections.Hashable):
            return dict.__getitem__(self, key)

        if set(key).issubset(self._viewkeys):
            if isinstance(key, collections.Sequence):
                return (self[k] for k in key)
            elif isinstance(key, collections.Set):
                return dictb((
                    (k, self[k]) for k in key
                ))
        raise KeyError(key)

    def __setitem__(self, key, value):
        """
        Hashable key -> sets key: value

            >>> d = dictb(a=1, b=2, c=3)
            >>> d['b'] = 22
            >>> d == dictb(a=1, b=22, c=3)
            True

        Sequence key -> sets key: value for zip(key, value)

            >>> d = dictb(a=1, b=2, c=3)
            >>> d[['a', 'c']] = 11, 33
            >>> d == dictb(a=11, b=2, c=33)
            True

        Set key -> sets same value for each key

            >>> d = dictb(a=1, b=2, c=3)
            >>> d[{'a', 'c'}] = 0
            >>> d == dictb(a=0, b=2, c=0)
            True
        """
        if isinstance(key, collections.Hashable):
            return dict.__setitem__(self, key, value)
        elif isinstance(key, collections.Sequence) and isinstance(value, collections.Sequence):
            return self.update({k: v for k, v in zip(key, value)})
        elif isinstance(key, collections.Iterable) or isinstance(key, collections.Iterator):
            return self.update({k: value for k in key})
        else:
            raise KeyError(key)

    def __delitem__(self, key):
        """
        Hashable key -> deletes key

            >>> d = dictb(a=1, b=2, c=3)
            >>> del d['b']
            >>> d == dictb(a=1, c=3)
            True

        Iterable key -> deletes keys

            >>> d = dictb(a=1, b=2, c=3)
            >>> del d[['a', 'c']]
            >>> d == dictb(b=2)
            True
        """
        if isinstance(key, collections.Hashable):
            return dict.__delitem__(self, key)

        keyset = set(key)
        if keyset.issubset(self._viewkeys):
            for k in keyset:
                del self[k]
        else:
            raise KeyError(key)

    # set operations

    def __sub__(self, other):
        """
            >>> dictb(a=1, b=2, c=3) - 'bcd' == dictb(a=1)
            True
            >>> dictb(a=1, b=2, c=3) - dictb(b=22, c=33, d=44) == dictb(a=1)
            True
        """
        return dictb(
            (k, self[k]) for k in self._viewkeys - set(other)
        )

    def __and__(self, other):
        """
            >>> dictb(a=1, b=2, c=3) & 'bcd' == dictb(b=2, c=3)
            True
            >>> dictb(a=1, b=2, c=3) & dictb(b=22, c=33, d=44) == dictb(b=2, c=3)
            True
        """
        return dictb((
            (k, self[k]) for k in self._viewkeys & set(other)
        ))

    def __rand__(self, other):
        """
            >>> 'bcd' & dictb(a=1, b=2, c=3) == {'b', 'c'}
            True
        """
        return set(other) & self._viewkeys

    def __or__(self, other):
        """
            >>> dictb(a=1, b=2, c=3) | 'bcd' == dictb(a=1, b=2, c=3, d=None)
            True
            >>> dictb(a=1, b=2, c=3) | dictb(b=22, c=33, d=44) == dictb(a=1, b=2, c=3, d=44)
            True
        """
        return dictb((
            (
                k,
                self[k] if k in self
                else
                other[k] if isinstance(other, collections.Mapping)
                else
                None
            )
            for k
            in self._viewkeys | set(other)
        ))

    def __ror__(self, other):
        """
            >>> 'bcd' | dictb(a=1, b=2, c=3) == {'a', 'b', 'c', 'd'}
            True
        """
        return set(other) | self._viewkeys

    def __xor__(self, other):
        """
            >>> dictb(a=1, b=2, c=3) ^ 'bcd' == dictb(a=1, d=None)
            True
            >>> dictb(a=1, b=2, c=3) ^ dictb(b=22, c=33, d=44) == dictb(a=1, d=44)
            True
        """
        return dictb((
            (
                k,
                self[k] if k in self
                else
                other[k] if isinstance(other, collections.Mapping)
                else
                None
            )
            for k
            in self._viewkeys ^ set(other)
        ))

    def __rxor__(self, other):
        """
            >>> 'bcd' ^ dictb(a=1, b=2, c=3) == {'a', 'd'}
            True
        """
        return set(other) ^ self._viewkeys

    # object

    def __repr__(self):
        return 'dictb(%s)' % dict.__repr__(self)
