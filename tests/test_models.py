# -*- coding: utf-8 -*-
import pytest
from server import models


class TestTag(object):
    def test_attributes(self):
        tag = models.Tag('tag-id', 'my-tag')

        assert tag.id == 'tag-id'
        assert tag.tag == 'my-tag'
        assert tag.taggings == []

    def test_taggings(self):
        tag = models.Tag('tag-id', 'my-tag')

        tagging = models.Tagging(1, 'shop-id', 'tag-id')

        assert tag.taggings == [tagging]

    def test_aggregator(self):
        tag = models.Tag('tag-id', 'my-tag')

        assert models.Tags['tag-id'] == tag
        assert models.Tags['tag']['my-tag'] == [tag]


class TestTagging(object):
    def test_attributes(self):
        tagging = models.Tagging('tagging-id', 'shop-id', 'tag-id')

        assert tagging.id == 'tagging-id'
        assert tagging.shop_id == 'shop-id'
        assert tagging.tag_id == 'tag-id'

        with pytest.raises(KeyError) as exc:
            tagging.tag

        assert "KeyError: 'tag-id'" in str(exc)

        with pytest.raises(KeyError) as exc:
            tagging.shop

        assert "KeyError: 'shop-id'" in str(exc)

    def test_shop(self):
        tagging = models.Tagging('tagging-id', 'shop-id', 'tag-id')

        shop = models.Shop('shop-id', 'shop-name', 1, 2)

        assert tagging.shop == shop

    def test_tag(self):
        tagging = models.Tagging('tagging-id', 'shop-id', 'tag-id')

        tag = models.Tag('tag-id', 'tag-name')

        assert tagging.tag == tag

    def test_aggregator(self):
        tagging = models.Tagging('tagging-id', 'shop-id', 'tag-id')

        assert models.Taggings['tagging-id'] == tagging
        assert models.Taggings['shop_id']['shop-id'] == [tagging]
        assert models.Taggings['tag_id']['tag-id'] == [tagging]


class TestShop(object):
    def test_attributes(self):
        shop = models.Shop('shop-id', 'shop-name', 1, 2)

        assert shop.id == 'shop-id'
        assert shop.name == 'shop-name'
        assert shop.lat == 1
        assert shop.lng == 2

        assert shop.taggings == []
        assert shop.products == []

    def test_taggings(self):
        shop = models.Shop('shop-id', 'shop-name', 1, 2)
        tagging = models.Tagging('tagging-id', 'shop-id', 'tag-id')

        assert shop.taggings == [tagging]

    def test_products(self, tagging):
        shop = models.Shop('shop-id', 'shop-name', 1, 2)
        product = models.Product('product-id', 'shop-id', 'product-title', .8, 10)

        assert shop.products == [product]

    def test_aggregator(self):
        shop = models.Shop('shop-id', 'shop-name', 1, 2)

        assert models.Shops['shop-id'] == shop
        assert len(models.Shops.indexes) == 0


class TestProduct(object):
    def test_attributes(self):
        product = models.Product('product-id', 'shop-id', 'product-title', .8, 10)

        assert product.id == 'product-id'
        assert product.shop_id == 'shop-id'
        assert product.title == 'product-title'
        assert product.popularity == .8
        assert product.quantity == 10

        with pytest.raises(KeyError) as exc:
            product.shop

        assert "KeyError: 'shop-id'" in str(exc)

    def test_shop(self):
        product = models.Product('product-id', 'shop-id', 'product-title', .8, 10)
        shop = models.Shop('shop-id', 'shop-name', 1, 2)

        assert product.shop == shop

    def test_aggregator(self):
        product = models.Product('product-id', 'shop-id', 'product-title', .8, 10)

        assert models.Products['product-id'] == product
        assert models.Products['shop_id']['shop-id'] == [product]


class TestIndexedAggregator(object):
    def test_clear(self, product):
        assert len(models.Products) == 1
        assert len(models.Products.indexes['shop_id']) == 1

        models.Products.clear()

        assert len(models.Products) == 0
        assert len(models.Products.indexes['shop_id']) == 0
