import json

from pymongo import MongoClient
from flask import Flask, request, abort
from flask_restx import Api, Resource, fields, reqparse

from common import *
from db_connect import DAO

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
api = Api(app=app, version='1.0', title='Twitty-API')


minting_tweet = api.model('MintingTweet', {
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
parser.add_argument('query', type=str, default={})
parser.add_argument('order', type=int, default=-1, choices=(-1, 1))
parser.add_argument('offset', type=int, default=0)
parser.add_argument('limit', type=int, default=10)
parser.add_argument('flag', type=str, default=None, choices=('invalid', 'outdated', 'processed'))


@api.route('/minting/tweets')
class MintingTweets(Resource):
    @api.marshal_list_with(minting_tweet)
    def get(self):
        args = parser.parse_args()
        print(args)
        ret = list(db.find('minting_tweets', json.loads(args['query'])).sort('created_at', args['order']).skip(args['offset']).limit(args['limit']))
        return ret


@api.route('/minting/tweets/search/<string:date>')
class MintingTweetsSearch(Resource):
    @api.marshal_list_with(minting_tweet)
    def get(self, data):
        pass


@api.route('/minting/tweets/<string:tid>')
class MintingTweetsOne(Resource):
    @api.marshal_with(minting_tweet)
    def get(self, tid):
        ret = db.find_one('minting_tweets', {'id': tid})
        return ret if ret else abort(*ERR_NOT_FOUND)


    @api.marshal_list_with(minting_tweet)
    def put(self, tid):
        args = parser.parse_args()
        ret = db.find_one_and_update('minting_tweets', {'id': tid}, {'$set': {args['flag']: True}})
        return [ret] if ret else abort(*ERR_NOT_FOUND)


@api.route('/minting/tweets/total')
class MintingTweetsTotal(Resource):
    def get(self):
        ret = db.countTotal('minting_tweets')
        return ret


@api.route('/minting/data/total')
class MintingDataTotal(Resource):
    def get(self):
        args = parser.parse_args()
        ret = db.count('minting_tweets', json.loads(args['query']))
        return ret


            


if __name__ == '__main__':
    app.run(debug=True, host=SERVICE_HOST, port=SERVICE_PORT)
