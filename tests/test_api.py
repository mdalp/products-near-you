# -*- coding: utf-8 -*-
from server import models


class TestSearchView(object):
    endpoint = '/search'

    def test_endpoint_exists(self, get):
        response = get(self.endpoint)
        assert response.status_code != 404

    def test_allowed_methods(self, client):
        all_methods = {
            'get', 'patch', 'head', 'post', 'put', 'options', 'trace', 'delete'
        }
        allowed_methods = {'get', 'head', 'options'}
        unallowed_methods = all_methods - allowed_methods

        for method in allowed_methods:
            method_handler = getattr(client, method)
            response = method_handler(self.endpoint)
            assert response.status_code != 405

        for method in unallowed_methods:
            method_handler = getattr(client, method)
            response = method_handler(self.endpoint)
            assert response.status_code == 405

    def test_products_in_response(self, get):
        """Check the response contains a key for products."""
        response = get('%s?%s' % (
            self.endpoint,
            'count=10&radius=500&position[lat]=59.33258&position[lng]=18.0649&tags=trousers&tags=shirts'
        ))

        assert response.status_code == 200
        assert 'products' in response.json
        assert isinstance(response.json['products'], list)

    def test_invalid_args(self, get):
        response = get('%s?%s' % (
            self.endpoint,
            'count=10&radius=500&position[lat]=59.33258&tags=trousers&tags=shirts'
        ))

        assert response.status_code == 400
        assert 'errors' in response.json
        assert response.json['errors'] == {u'position': {u'lng': [u'Field may not be null.']}}

    def test_returns(self, get):
        shop = models.Shop('shop-id', 'shop-name', 59.33258, 18.0649)
        product = models.Product('product-id', shop.id, 'product-title', .8, 10)
        tag = models.Tag('tag-id', 'trousers')
        tagging = models.Tagging('tagging-id', shop.id, tag.id)

        response = get('%s?%s' % (
            self.endpoint,
            'count=10&radius=500&position[lat]=59.33258&position[lng]=18.0649&tags=trousers&tags=shirts'
        ))

        assert response.status_code == 200
        assert 'products' in response.json
        assert response.json['products'] == [
            {
                'shop': {'lat': 59.33258, 'lng': 18.0649},
                'title': 'product-title',
                'popularity': .8,
            }
        ]





