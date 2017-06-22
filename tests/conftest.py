# -*- coding: utf-8 -*-

import json
import functools
import os
import sys

import pytest
from flask import Flask

# Set up the path to import from `server`.
root = os.path.join(os.path.dirname(__file__))
package = os.path.join(root, '..')
sys.path.insert(0, os.path.abspath(package))

from server import models
from server.app import create_app


class TestResponseClass(Flask.response_class):
    @property
    def json(self):
        return json.loads(self.data)


Flask.response_class = TestResponseClass


def humanize_werkzeug_client(client_method):
    """Wraps a `werkzeug` client method (the client provided by `Flask`) to make
    it easier to use in tests.

    """
    @functools.wraps(client_method)
    def wrapper(url, **kwargs):
        # Always set the content type to `application/json`.
        kwargs.setdefault('headers', {}).update({
            'content-type': 'application/json'
        })

        # If data is present then make sure it is json encoded.
        if 'data' in kwargs:
            data = kwargs['data']
            if isinstance(data, dict):
                kwargs['data'] = json.dumps(data)

        kwargs['buffered'] = True

        return client_method(url, **kwargs)

    return wrapper


@pytest.yield_fixture(scope='session', autouse=True)
def app():
    """An application for the tests."""
    parent = os.path.dirname(__file__)
    data_path = os.path.join(parent, '..', 'data')

    _app = create_app({
        'TESTING': True,
        'DATA_PATH': data_path,
    })
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='function')
def client(app, request):
    return app.test_client()


@pytest.fixture(scope='function')
def get(client):
    return humanize_werkzeug_client(client.get)


@pytest.fixture(scope='function', autouse=True)
def clear_index_aggregations():
    for model_name, model in models.__dict__.items():
        if isinstance(model, models.IndexedAggregator):
            model.clear()


@pytest.fixture(scope='function')
def tag():
    return models.Tag('tag-id', 'my-tag')


@pytest.fixture(scope='function')
def tagging():
    return models.Tagging('tagging-id', 'shop-id', 'tag-id')


@pytest.fixture(scope='function')
def shop():
    return models.Shop('shop-id', 'shop-name', 1, 2)


@pytest.fixture(scope='function')
def product():
    return models.Product('product-id', 'shop-id', 'product-title', 0.8, 10)
