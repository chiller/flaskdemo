from flask import Flask, jsonify, abort
from flask.ext.restful import Api, Resource
from flask.ext.restful import reqparse, marshal, fields

app = Flask(__name__)

api = Api(app)

users = [
    {"id": 1, "name": "user1", "email": "user1@example.com", "password":"dsa"},
    {"id": 2, "name": "user2", "email": "user2@example.com", "password":"dsa"},
]
user_fields = {
    'name': fields.String,
    'email': fields.String,
    'uri': fields.Url('user')
}

class UserListAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True,
                help='No user name provided', location='json')
        self.reqparse.add_argument('password', type=str, required=True, location='json')
        self.reqparse.add_argument('email', type=str, default="", location='json')
        super(UserListAPI, self).__init__()


    def get(self):
        return [marshal(user, user_fields) for user in users]

    def post(self):
        args = self.reqparse.parse_args()
        user = {
            'id': users[-1]['id'] + 1,
            'name': args['name'],
            'email': args['email']
        }
        users.append(user)
        return marshal(user, user_fields), 201


class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=False, location='json')
        self.reqparse.add_argument('email', type=str, required=False, location='json')
        super(UserAPI, self).__init__()

    def get_object_or_404(self, id):
        user = filter(lambda x: x['id'] == id, users)
        if len(user) == 0:
            abort(404)
        return user[0]

    def get(self, id):
        return marshal(self.get_object_or_404(id), user_fields), 200

    def put(self, id):
        user = self.get_object_or_404(id)
        args = self.reqparse.parse_args()
        user['name'] = args['name']
        user['email'] = args['email']
        return marshal(user, user_fields), 200

    def patch(self, id):
        user = self.get_object_or_404(id)
        args = self.reqparse.parse_args()
        user['name'] = args.get('name') or user['name']
        user['email'] = args.get('email') or user['email']
        return marshal(user, user_fields), 200

    def delete(self, id):
        user = self.get_object_or_404(id)
        users.remove(user)
        return '', 204

api.add_resource(UserListAPI, '/users', endpoint='users')
api.add_resource(UserAPI, '/users/<int:id>', endpoint='user')


if __name__ == '__main__':
    app.run(debug=True)
