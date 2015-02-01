import re
from flask.ext.restful import fields, Resource, reqparse, marshal, abort
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask import Flask
from flask.ext.restful import Api, Resource
from werkzeug.security import generate_password_hash


app = Flask(__name__)


if os.environ.get('TESTING'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'


db = SQLAlchemy(app)
db.create_all()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120), unique=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.name


user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
    'uri': fields.Url('user')
}


class UserListAPI(Resource):

    @staticmethod
    def valid_email(value):
        pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(pattern, value):
            raise ValueError("Email is not valid.")
        return value

    @staticmethod
    def valid_password(value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters in length.")
        return value

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True,
                help='No user name provided', location='json')
        self.reqparse.add_argument('password',
                                   type=self.valid_password,
                                   required=True,
                                   location='json')
        self.reqparse.add_argument('email',
                                   type=self.valid_email,
                                   required=True,
                                   location='json')
        super(UserListAPI, self).__init__()


    def get(self):
        return [marshal(user, user_fields) for user in User.query.all()]

    def post(self):
        args = self.reqparse.parse_args()
        user = User(args['name'], args['email'], generate_password_hash(args['password']))
        db.session.add(user)
        db.session.commit()
        return marshal(user, user_fields), 201


class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=False, location='json')
        self.reqparse.add_argument('email', type=str, required=False, location='json')
        super(UserAPI, self).__init__()

    def get_object_or_404(self, id):
        user = User.query.filter_by(id=id).all()
        if len(user) == 0:
            abort(404)
        return user[0]

    def get(self, id):
        return marshal(self.get_object_or_404(id), user_fields), 200

    def put(self, id):
        user = self.get_object_or_404(id)
        args = self.reqparse.parse_args()
        user.name = args['name']
        user.email = args['email']
        db.session.add(user)
        db.session.commit()
        return marshal(user, user_fields), 200

    def patch(self, id):
        user = self.get_object_or_404(id)
        args = self.reqparse.parse_args()
        user.name = args.get('name') or user.name
        user.email = args.get('email') or user.email
        db.session.add(user)
        db.session.commit()
        return marshal(user, user_fields), 200

    def delete(self, id):
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return '', 204

def create_api(app):
    api = Api(app)
    api.add_resource(UserListAPI, '/users', endpoint='users')
    api.add_resource(UserAPI, '/users/<int:id>', endpoint='user')

create_api(app)

#TODO: update password

if __name__ == '__main__':
    app.run(debug=True)

