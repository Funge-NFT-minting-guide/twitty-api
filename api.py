from pymongo import MongoClient
from flask import Flask, request, abort
from flask_restx import Api, Resource, fields, reqparse

from db_connect import DAO

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
api = Api(app=app, version='1.0', title='Twitty-API')


minting = api.model('Minting', {
    '_id': fields.String(readonly=True),
    'id': fields.String(readonly=True),
    'created_at': fields.DateTime(),
    'text': fields.String(),
    'user': fields.String(),
    'uid': fields.String(),
    'profile_image_url': fields.String(),
    'followers': fields.Integer(),
    'url': fields.String(),
    'invalid': fields.Boolean(),
    'outdated': fields.Boolean(),
    'processed': fields.Boolean()
    })


db = DAO('twitty')

parser = reqparse.RequestParser()
parser.add_argument('query', type=dict, default={}, location='json')
parser.add_argument('order', type=int, default=-1, choices=(-1, 1))
parser.add_argument('offset', type=int, default=0)
parser.add_argument('max_limit', type=int, default=10)


@api.route('/minting/tweets')
class MintingTweets(Resource):
    @api.marshal_list_with(minting)
    def get(self):
        args = parser.parse_args()
        return list(db.find('minting_tweets', args['query']).sort('created_at', args['order']).skip(args['offset']).limit(args['max_limit']))


@api.route('/minting/tweets/search/<string:date>')
class MintingTweetsSearch(Resource):
    @api.marshal_list_with(minting)
    def get(self, data):
        pass


@api.route('/minting/tweets/<string:_id>')
class MintingTweetsOne(Resource):
    @api.marshal_with(minting)
    def get(self, _id):
        ret = db.find_one('minting_tweets', {'id': _id})
        print(ret)
        return [ret] if ret else abort(404, 'No result found.')
            


if __name__ == '__main__':
    app.run(debug=True)
