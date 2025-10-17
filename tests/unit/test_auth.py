import unittest
from app import create_app, db
from app.models.user import User
import json

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()

        # DB tabloları
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_success(self):
        response = self.client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "123456"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("User registered successfully", response.get_data(as_text=True))

    def test_register_missing_fields(self):
        response = self.client.post("/auth/register", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email and password required", response.get_data(as_text=True))

    def test_login_success(self):
        with self.app.app_context():
            user = User(email="test@example.com")
            user.set_password("123456")
            db.session.add(user)
            db.session.commit()

        response = self.client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "123456"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
