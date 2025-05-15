import unittest
from app import create_app
from app.models import db, User, FuelType, UploadBatch, PriceRecord
from app.models import db, User
from flask import current_app
from itsdangerous import URLSafeTimedSerializer

# Test suite for authentication-related functionality
class AuthTestCase(unittest.TestCase):
    # Runs before each test
    def setUp(self):
        # Create Flask app using factory
        self.app = create_app()
        self.app.config['TESTING'] = True  # Enable testing mode
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory DB
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for test requests

        self.client = self.app.test_client()  # Simulated client for sending requests

        # Create tables in test DB
        with self.app.app_context():
            db.create_all()

    # Runs after each test to clean up DB
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.session.remove()
        db.drop_all()

    # Test: New user registration should succeed
    def test_register_success(self):
        response = self.client.post('/signup', data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)

    # Test: Registration with an existing email should fail
    def test_register_duplicate_email(self):
        # First registration
        self.client.post('/signup', data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        })
        # Attempt to register again with same email
        response = self.client.post('/signup', data={
            'first_name': 'Test2',
            'last_name': 'User2',
            'email': 'testuser@example.com',
            'password': 'AnotherPass123'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'fail', response.data)

    # Test: Login should succeed with correct credentials
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
        self.assertIn(b'success', response.data)

    # Test: Login should fail with incorrect password
    def test_login_wrong_password(self):
        self.client.post('/signup', data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'Test@1234'
        })
        response = self.client.post('/login', data={
            'email': 'testuser@example.com',
            'password': 'WrongPass123'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'error', response.data)

    # Test: Login should fail with unregistered email
    def test_login_unregistered_email(self):
        response = self.client.post('/login', data={
            'email': 'nouser@example.com',
            'password': 'AnyPassword123'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'error', response.data)

    # Test: Logout should redirect (simulate user login first)
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
        self.assertIn('/', response.location)  # Logout redirects to home page

    # Test: Token should generate successfully for password reset
    def test_password_reset_token_generation(self):
        with self.app.app_context():
            user = User(
                first_name="Test",
                last_name="User",
                username="Test User",
                email="testuser@example.com",
                verified=False  # Required due to NOT NULL constraint
            )
            user.set_password("Test@1234")
            db.session.add(user)
            db.session.commit()

            # Generate secure token with secret key
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = serializer.dumps({'user_id': user.id})
            self.assertIsNotNone(token)

    # Test: Accessing password reset page with invalid token should redirect
    def test_password_reset_with_invalid_token(self):
        response = self.client.get('/reset-password/invalidtoken')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    # Test: Email verification with invalid token should redirect
    def test_email_verification_with_invalid_token(self):
        response = self.client.get('/verify-email/invalidtoken')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

# Entry point to run tests
if __name__ == '__main__':
    unittest.main()
