import unittest
from app import create_app, db
from app.models import User
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_success(self):
        response = self.client.post('/signup', data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"status": "success"', response.data)

    def test_register_duplicate_email(self):
        self.client.post('/signup', data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        })
        response = self.client.post('/signup', data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'AnotherTest@1234'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'"status": "fail"', response.data)

    def test_login_success(self):
        self.client.post('/signup', data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        })
        response = self.client.post('/login', data={
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"status": "success"', response.data)

    def test_login_wrong_password(self):
        self.client.post('/signup', data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        })
        response = self.client.post('/login', data={
            'email': 'testuser@example.com',
            'password': 'WrongPass@1234'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'"status": "error"', response.data)

    def test_login_unregistered_email(self):
        response = self.client.post('/login', data={
            'email': 'unregistered@example.com',
            'password': 'Test@1234'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'"status": "error"', response.data)

    def test_logout(self):
        self.client.post('/signup', data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        })
        self.client.post('/login', data={
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        })
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)

    def test_password_reset_token_generation(self):
        user = User(first_name="Test", last_name="User", username="Test User", email="testuser@example.com")
        user.set_password("Test@1234")
        db.session.add(user)
        db.session.commit()

        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps({'user_id': user.email})
        self.assertIsNotNone(token)

    def test_password_reset_with_invalid_token(self):
        response = self.client.get('/reset-password/invalidtoken')
        self.assertEqual(response.status_code, 302)
        self.assertIn(b'Invalid or expired token', response.data)

    def test_email_verification_with_invalid_token(self):
        response = self.client.get('/verify-email/invalidtoken')
        self.assertEqual(response.status_code, 302)
        self.assertIn(b'Invalid or expired token', response.data)

if __name__ == '__main__':
    unittest.main()
