# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request, abort, make_response
from flask_cors import CORS

from . import utils

api = Blueprint('api', __name__)

CORS(api)


@api.route('/search', methods=['GET'])
def search():
    data, errors = utils.clean_args(request.args)
    if errors:
        abort(make_response(jsonify({'errors': errors}), 400))

    products = utils.find_products(data)
    formatted_products = utils.format_products(products)

    return jsonify({'products': formatted_products})
