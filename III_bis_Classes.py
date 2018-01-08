from collections import OrderedDict, Callable, defaultdict


class DefaultOrderedDict(OrderedDict):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        # self[key] = value = self.default_factory()
        # return value
        return self.default_factory()  # Petite variation par rapport au code originel

    """
    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))
    """

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                               OrderedDict.__repr__(self))


class SortedDict(OrderedDict):
    def __setitem__(self, key, value):
        try:
            int(key)
        except:
            raise TypeError('key cannot be converted into int')

        if len(self) == 0:
            super().__setitem__(int(key), value)
        else:
            if int(key) > next(reversed(self)):
                super().__setitem__(int(key), value)
            else:
                i = 0
                while int(key) > list(self.keys())[i]:
                    i += 1
                super().__setitem__(int(key), value)
                for _ in range(len(self.keys()) - i - 1):
                    super().move_to_end(list(self.keys())[i])

    def __repr__(self):
        return 'SortedDict(%s)' % (OrderedDict.__repr__(self))


class DefaultSortedDict(SortedDict):
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
                not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        super().__init__(*a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, int(key))
        except KeyError:
            return self.__missing__(key)
        except ValueError:
            return ValueError('Cannot convert key into integer')

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        # self[key] = value = self.default_factory()
        # return value
        return self.default_factory()  # Petite variation par rapport au code originel

    def __repr__(self):
        return 'DefaultSortedDict(%s, %s)' % (self.default_factory,
                                              SortedDict.__repr__(self))


class InvertedIndex(DefaultOrderedDict):
    @staticmethod
    def inverted_index_factory():
        return {'idf': 0, 'tf': defaultdict(int)}

    def __init__(self, *a, **kw):
        super().__init__(default_factory=InvertedIndex.inverted_index_factory)
        data_dict = dict(*a, **kw)
        for term in data_dict:
            self[term] = {} # étape nécessaire, car l'ordered dict utilisé ne garde pas les clés absentes demandées
            self[term]['idf'] = data_dict[term]['idf']
            self[term]['tf'] = defaultdict(int, data_dict[term]['tf'])


class DocumentDict(DefaultSortedDict): # Non utilisé, peu performant
    def __init__(self, *a, **kw):
        data_dict=dict(*a,**kw)
        super().__init__(int, sorted(data_dict.items(), key=lambda x : x[0]))

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, str(key))  # Petite modification
        except KeyError:
            return self.__missing__(key)
        except ValueError:
            return ValueError('Cannot convert key into integer')


if __name__ == "__main__":

    a = InvertedIndex()
    print(a)
    print(a['blublu']['idf'])
    for k in a['blublu']['tf']:
        print(k)
    print(a.keys())
    b = InvertedIndex({'blublu': {'idf': 2, 'tf': {"2": 2, "1": 4}}})
    print(b)
    print(b['blublu'])
    print(b['blabla'])
    print(b['blublu']['tf']['3'])

    c = DocumentDict({2: "Romeo", "1": "Juliet"})
    print(c)
    c['0'] = "Marta"
    c['20000'] = "Samanta"
    print(c)
    print(c[3])
