from flask import json
import userflask
import unittest

class UserAPITest(unittest.TestCase):

    def setUp(self):
        userflask.app.config['TESTING'] = True
        self.app = userflask.app.test_client()

    def test_list(self):
        response = self.app.get('/users')
        data = json.loads(response.data)
        assert response.status_code == 200
        assert len(data)

    def test_create(self):
        assert len(userflask.users) == 2
        response = self.app.post('/users',
                                 data=json.dumps({"name": "doge",
                                                  "email": "doge@wow.com",
                                                  "password": "toge"}),
                                 content_type='application/json')
        self.assertEquals(response.status_code, 201, response.data)
        assert json.loads(response.data)['uri']
        assert len(userflask.users) == 3

    def test_get(self):
        response = self.app.get('/users/1')
        data = json.loads(response.data)
        assert data['uri']
        assert data['email']
        assert "password" not in data

    def test_update(self):
        self.app.put('/users/1',
                                data=json.dumps({"name": "doge",
                                                  "email": "doge@wow.com"}),
                                content_type='application/json')
        response = self.app.get('/users/1')
        data = json.loads(response.data)
        self.assertEquals(data['name'], "doge")

    def test_patch(self):
        response = self.app.patch('/users/1',
                                data=json.dumps({"name": "doge"}),
                                content_type='application/json')
        response = self.app.get('/users/1')
        data = json.loads(response.data)
        self.assertEquals(data['name'], "doge")
        self.assertEquals(data['email'], "user1@example.com")

    def test_delete(self):
        response = self.app.delete('/users/2')
        assert response.status_code == 204
        response = self.app.get('/users/2')
        assert response.status_code == 404


if __name__ == '__main__':
    unittest.main()