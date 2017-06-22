# -*- coding: utf-8 -*-
from werkzeug.datastructures import ImmutableMultiDict

from server import models, utils


class TestCleanArgs(object):
    def test_with_tags(self):
        res = ImmutableMultiDict([
            ('count', u'10'),
            ('position[lat]', u'59.33258'),
            ('position[lng]', u'18.0649'),
            ('radius', u'500'),
            ('tags', u'blah'),
            ('tags', u'bluh')
        ])

        assert utils.clean_args(res) == ({
            'count': 10,
            'position': {'lat': 59.33258, 'lng': 18.0649},
            'radius': 500,
            'tags': [u'blah', u'bluh']
        }, {})

    def test_without_tags(self):
        res = ImmutableMultiDict([
            ('count', u'10'),
            ('position[lat]', u'59.33258'),
            ('position[lng]', u'18.0649'),
            ('radius', u'500'),
        ])

        assert utils.clean_args(res) == ({
            'count': 10,
            'position': {'lat': 59.33258, 'lng': 18.0649},
            'radius': 500,
            'tags': []
        }, {})


class TestFindCloseShops(object):
    def test_with_tags(self):
        # Will be retrieved
        tag = models.Tag('tag-id', 'tag-name')
        shop = models.Shop('shop-id', 'shop-name', 1, 2)
        models.Tagging('tagging-id', shop.id, tag.id)

        # Wont be retrieved
        tag2 = models.Tag('tag-id-2', 'tag-name-2')
        shop2 = models.Shop('shop-id-2', 'shop-name-2', 1, 2)
        models.Tagging('tagging-id-2', shop2.id, tag2.id)

        position = utils.Position(1, 2)
        radius = 3
        tags = ['tag-name']
        shops = utils._find_close_shops(position, radius, tags)

        assert shops == [shop]

    def test_without_tags(self):
        """The function if not specifying tags returns all shops within radius."""
        # Will be retrieved
        tag = models.Tag('tag-id', 'tag-name')
        shop = models.Shop('shop-id', 'shop-name', 1, 2)
        models.Tagging('tagging-id', shop.id, tag.id)

        # Will be retrieved
        tag2 = models.Tag('tag-id-2', 'tag-name-2')
        shop2 = models.Shop('shop-id-2', 'shop-name-2', 1, 2)
        models.Tagging('tagging-id-2', shop2.id, tag2.id)

        position = utils.Position(1, 2)
        radius = 3
        shops = utils._find_close_shops(position, radius)

        assert sorted(shops) == sorted([shop, shop2])

    def test_exclude_outside_radius(self):
        # Will be retrieved
        tag = models.Tag('tag-id', 'tag-name')
        shop = models.Shop('shop-id', 'shop-name', 1, 2)
        models.Tagging('tagging-id', shop.id, tag.id)

        # Wont be retrieved because it's outside radius
        tag2 = models.Tag('tag-id-2', 'tag-name-2')
        shop2 = models.Shop('shop-id-2', 'shop-name-2', 5, 10)
        models.Tagging('tagging-id-2', shop2.id, tag2.id)

        position = utils.Position(1, 2)
        radius = 3
        shops = utils._find_close_shops(position, radius)

        assert shops == [shop]


class TestFindBestProducts(object):
    def test_products(self):
        shop = models.Shop('shop-id', 'shop-name', 1, 2)
        shop2 = models.Shop('shop-id-2', 'shop-name-2', 5, 10)
        # generate some products for `shop`
        for i in range(1, 10, 2):
            models.Product('product-id-%d' % i, shop.id, 'product-title', .1 * i, 10)

        # generate some products for `shop2`
        for i in range(2, 11, 2):
            models.Product('product-id-%d' % i, shop2.id, 'product-title', .1 * i, 10)

        products = utils._find_best_products(models.Shops.values(), 3)

        assert products == [
            models.Products['product-id-10'],
            models.Products['product-id-9'],
            models.Products['product-id-8'],
        ]


class TestLoadModel(object):
    def test_everything_loaded(self, app):
        # Aggregator is empty at first
        assert len(models.Tags) == 0

        tag_number = utils.load_model(app, models.Tag, 'tags.csv')
        # then it's populated
        assert len(models.Tags) == tag_number
