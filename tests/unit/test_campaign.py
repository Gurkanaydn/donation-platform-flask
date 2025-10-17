import unittest
from app import create_app, db
from app.models.user import User
from flask_jwt_extended import create_access_token
import json

class CampaignTestCase(unittest.TestCase):
    def setUp(self):
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Test user
            self.user = User(email="user@example.com")
            self.user.set_password("123456")
            db.session.add(self.user)
            db.session.commit()  # user.id oluşsun

            # JWT
            self.token = create_access_token(identity=str(self.user.id))

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_campaign(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "title": "Test Campaign",
            "description": "Test description",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31"
        }

        response = self.client.post("/api/campaigns/", json=payload, headers=headers)
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["title"], "Test Campaign")
