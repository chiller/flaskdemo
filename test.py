import json
import unittest
from flask.ext.testing import TestCase
import os
from werkzeug.security import generate_password_hash, check_password_hash

os.environ['TESTING'] = 'True'

from userflask import app, db, User


class SQLAlchemyTest(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        admin = User('admin', 'admin@example.com', "dsadasdsa")
        user = User("user", "wow@ada.ds", "dsadas")
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_list(self):
        response = self.client.get('/users')
        data = json.loads(response.data)
        assert response.status_code == 200
        assert len(data)

    def test_create(self):
        self.assertEqual(len(User.query.all()), 2)
        response = self.client.post('/users',
                                 data=json.dumps({"name": "doge",
                                                  "email": "doge@wow.com",
                                                  "password": "togetoge"}),
                                 content_type='application/json')
        self.assertEquals(response.status_code, 201, response.data)
        assert json.loads(response.data)['uri']
        self.assertEqual(len(User.query.all()), 3)

    def test_get(self):
        response = self.client.get('/users/1')
        data = json.loads(response.data)
        assert data['id']
        assert data['email']
        assert "password" not in data

    def test_update(self):
        self.client.put('/users/1',
                     data=json.dumps({"name": "doge",
                                      "email": "doge@wow.com"}),
                     content_type='application/json')
        response = self.client.get('/users/1')
        data = json.loads(response.data)
        self.assertEquals(data['name'], "doge")

    def test_patch(self):
        response = self.client.patch('/users/1',
                                  data=json.dumps({"name": "doge"}),
                                  content_type='application/json')
        response = self.client.get('/users/1')
        data = json.loads(response.data)
        self.assertEquals(data['name'], "doge")
        self.assertEquals(data['email'], "admin@example.com")

    def test_delete(self):
        response = self.client.delete('/users/2')
        assert response.status_code == 204
        response = self.client.get('/users/2')
        assert response.status_code == 404

    def test_head(self):
        response = self.client.head('/users/1')
        assert response.status_code == 200


    def test_hasher(self):
        phash = generate_password_hash("password")
        assert check_password_hash(phash, "password")

    def test_short_password(self):
        response = self.client.post('/users',
                                 data=json.dumps({"name": "doge",
                                                  "email": "doge@wow.com",
                                                  "password": "toge"}),
                                 content_type='application/json')
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data, '{"message": "Password must be at least 8 characters in length."}')

    def test_bad_email(self):
        response = self.client.post('/users',
                                 data=json.dumps({"name": "doge",
                                                  "email": "wow.com",
                                                  "password": "togetoge"}),
                                 content_type='application/json')
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data, '{"message": "Email is not valid."}')

if __name__ == '__main__':
    unittest.main()