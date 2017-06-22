# -*- coding: utf-8 -*-
import bisect
import csv
import math
from collections import namedtuple
from operator import attrgetter, itemgetter

from flask import current_app
from marshmallow import Schema, fields

from . import models

Position = namedtuple('Position', 'lat,lng')


def data_path(app, filename):
    data_path = app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)


class PositionSchema(Schema):
    lat = fields.Float()
    lng = fields.Float()


class ProductSearchSchema(Schema):
    count = fields.Integer(required=True)
    radius = fields.Float(required=True)
    position = fields.Nested(PositionSchema, required=True)
    tags = fields.List(fields.String())


def clean_args(args):
    """Format in a more meaningful way the args and validate them.

    Args:
        args(ImmutableDict): `request.args` given by Flask

    Returns:
        (dict, dict) a tuple of a dict of `cleaned_data` and a dict of errors.
    """
    cleaned_dict = {
        'count': args.get('count'),
        'radius': args.get('radius'),
        'position': {
            'lat': args.get('position[lat]'),
            'lng': args.get('position[lng]'),
        },
        'tags': args.getlist('tags'),
    }
    data, errors = ProductSearchSchema().load(cleaned_dict)
    return data, errors


def _distance(pos1, pos2):
    """Calculate distance between two points.

    NOTES:
        I multiply by 1000 to take it to a better scale.
        In theory it would be needed a research in order to be sure
        on what the scale should be.
    """
    return 1000 * math.hypot(
        float(pos1.lat) - float(pos2.lat),
        float(pos1.lng) - float(pos2.lng)
    )


def _find_close_shops(position, radius, tags=None):

    tagged_shops = set()

    if tags and len(tags) > 0:
        for tag in tags:
            try:
                taggings = models.Tags['tag'][tag][0].taggings
            except KeyError:
                # if the tag doesn't exist it trows a KeyError.
                # lets handle it and skip the tag.
                continue
            shops = map(attrgetter('shop'), taggings)
            tagged_shops |= set(shops)
    else:
        tagged_shops = models.Shops.values()

    shops = []
    for shop in tagged_shops:
        if _distance(position, shop) <= radius:
            shops.append(shop)
    return shops


def _find_best_products(shops, count):
    """Find the `count` products in `shops` with best popularity.

    NOTES:
        Performances of this method could be improved checking
        if to insert a new product in the list or not instead of
        adding it and then deliting.
    """
    products = []
    for i, shop in enumerate(shops):
        for product in shop.products:
            if len(products) == count and products[0][0] > product.popularity:
                continue
            bisect.insort(products, (product.popularity, product))
            if len(products) > count:
                del products[0]

    return map(itemgetter(1), reversed(products))


def find_products(data):
    """Find products matching the search."""
    position = Position(**data['position'])
    radius = data['radius']
    tags = data['tags']
    shops = _find_close_shops(position, radius, tags)

    count = data['count']
    products = _find_best_products(shops, count)
    return products


def format_products(products):
    formatted_products = []
    for product in products:
        formatted_products.append({
            'shop': {'lat': product.shop.lat, 'lng': product.shop.lng},
            'title': product.title,
            'popularity': product.popularity,
        })
    return formatted_products


def load_model(app, model_class, filename):
    filename = data_path(app, filename)
    count = 0

    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            model_class(**row)
            count += 1
    return count


