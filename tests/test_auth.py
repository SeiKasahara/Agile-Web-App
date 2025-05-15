import unittest
from unittest.mock import patch
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from app import create_app
from app.models import db, User
from app.routes.auth import generate_reset_token

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SECRET_KEY'] = 'test-secret-key'  # for itsdangerous

        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def test_register_success(self):
        rv = self.client.post(
            '/signup',
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'password': 'Test@1234'
            }
        )
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'success', rv.data)

    def test_register_duplicate_email(self):
        self.client.post(
            '/signup',
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'password': 'Test@1234'
            }
        )
        rv = self.client.post(
            '/signup',
            data={
                'first_name': 'Test2',
                'last_name': 'User2',
                'email': 'test@example.com',
                'password': 'Another@123'
            }
        )
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'fail', rv.data)

    def test_login_success(self):
        self.client.post(
            '/signup',
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'login@example.com',
                'password': 'Login@123'
            }
        )
        rv = self.client.post(
            '/login',
            data={'email': 'login@example.com', 'password': 'Login@123'}
        )
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'success', rv.data)

    def test_login_wrong_password(self):
        self.client.post(
            '/signup',
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'wrongpass@example.com',
                'password': 'Right@123'
            }
        )
        rv = self.client.post(
            '/login',
            data={'email': 'wrongpass@example.com', 'password': 'Nope@123'}
        )
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'error', rv.data)

    def test_login_unregistered_email(self):
        rv = self.client.post(
            '/login',
            data={'email': 'nouser@example.com', 'password': 'Anything@1'}
        )
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'error', rv.data)

    def test_logout(self):
        self.client.post(
            '/signup',
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'logout@example.com',
                'password': 'Logout@123'
            }
        )
        self.client.post(
            '/login',
            data={'email': 'logout@example.com', 'password': 'Logout@123'}
        )
        rv = self.client.get('/logout')
        self.assertEqual(rv.status_code, 302)
        self.assertIn('/', rv.location)

    def test_password_reset_token_generation(self):
        with self.app.app_context():
            user = User(
                first_name='Foo',
                last_name='Bar',
                username='Foo Bar',
                email='foo@bar.com',
                verified=False
            )
            user.set_password('Abc@1234')
            db.session.add(user)
            db.session.commit()

            token = generate_reset_token(user)
            self.assertIsInstance(token, str)
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            data = s.loads(token, max_age=3600)
            self.assertEqual(data.get('user_id'), user.id)

    def test_password_reset_with_invalid_token(self):
        rv = self.client.get('/reset-password/invalidtoken')
        self.assertEqual(rv.status_code, 302)
        self.assertIn('/login', rv.location)

    def test_forgot_password_no_email(self):
        rv = self.client.post('/forgot-password', data={})
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'Email is required', rv.data)

    def test_forgot_password_invalid_email(self):
        rv = self.client.post(
            '/forgot-password',
            data={'email': 'noone@nowhere.com'}
        )
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'Invalid email', rv.data)

    def test_set_password(self):
        self.client.post(
            '/signup',
            data={
                'first_name': 'Set',
                'last_name': 'Pass',
                'email': 'setpass@example.com',
                'password': 'Orig@123'
            }
        )
        self.client.post(
            '/login',
            data={'email': 'setpass@example.com', 'password': 'Orig@123'}
        )
        rv = self.client.post(
            '/set-password',
            data={'new_password': 'New@12345'}
        )
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Password set successfully', rv.data)

if __name__ == '__main__':
    unittest.main()
