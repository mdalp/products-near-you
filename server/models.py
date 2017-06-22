# -*- coding: utf-8 -*-
from collections import defaultdict

from werkzeug.utils import cached_property


class IndexedAggregator(dict):
    def __init__(self, indexes=None):
        indexes_names = indexes or set()
        self.indexes = {}

        for index in indexes_names:
            self.indexes[index] = defaultdict(set)

    def add(self, val):
        self[val.id] = val
        for index_name, index in self.indexes.items():
            # add reference of the object in all indexes.
            index[getattr(val, index_name)].add(val.id)

    def __getitem__(self, key):
        if key not in self.indexes:
            return super(IndexedAggregator, self).__getitem__(key)

        index = self.indexes[key]
        # TODO: cache this.
        values = {
            key: [self[object_id] for object_id in object_ids]
            for key, object_ids in index.items()
            if len(object_ids) > 0
        }

        return values

    def __delitem__(self, key):
        item = self[key]
        super(IndexedAggregator, self).__delitem__(key)

        for index_name, index in self.indexes.items():
            index_key = getattr(item, index_name)
            index[index_key].discard(key)
            if len(index[index_key]) == 0:
                del index[index_key]

    def clear(self):
        for key in self.keys():
            del self[key]


class Tag(object):
    def __init__(self, id, tag):
        self.id = id
        self.tag = tag
        Tags.add(self)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.tag)

    @cached_property
    def taggings(self):
        try:
            return Taggings['tag_id'][self.id]
        except KeyError:
            return []


class Tagging(object):
    def __init__(self, id, shop_id, tag_id):
        self.id = id
        self.shop_id = shop_id
        self.tag_id = tag_id
        Taggings.add(self)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.shop_id[:8], self.tag_id[:8])

    @cached_property
    def tag(self):
        return Tags[self.tag_id]

    @cached_property
    def shop(self):
        return Shops[self.shop_id]


class Shop(object):
    def __init__(self, id, name, lat, lng):
        self.id = id
        self.name = name
        self.lat = lat
        self.lng = lng
        Shops.add(self)

    @cached_property
    def taggings(self):
        try:
            return Taggings['shop_id'][self.id]
        except KeyError:
            return []

    @cached_property
    def products(self):
        try:
            return Products['shop_id'][self.id]
        except KeyError:
            return []


class Product(object):
    def __init__(self, id, shop_id, title, popularity, quantity):
        self.id = id
        self.shop_id = shop_id
        self.title = title
        self.popularity = popularity
        self.quantity = quantity
        Products.add(self)

    @cached_property
    def shop(self):
        return Shops[self.shop_id]


Tags = IndexedAggregator(('tag',))
Taggings = IndexedAggregator(('shop_id', 'tag_id'))
Shops = IndexedAggregator()
Products = IndexedAggregator(('shop_id',))
