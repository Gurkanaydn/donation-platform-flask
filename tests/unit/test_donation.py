import unittest
from app import create_app, db
from app.models.user import User
from app.models.campaign import Campaign
from flask_jwt_extended import create_access_token
from datetime import datetime
import json

class DonationTestCase(unittest.TestCase):
    def setUp(self):
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            self.user = User(email="user@example.com")
            self.user.set_password("123456")
            db.session.add(self.user)
            db.session.commit()

            self.campaign = Campaign(
                title="Test Campaign",
                description="Desc",
                start_date=datetime.strptime("2025-01-01", "%Y-%m-%d").date(),
                end_date=datetime.strptime("2025-12-31", "%Y-%m-%d").date(),
                created_by=self.user.id,
                is_delete=False
            )
            db.session.add(self.campaign)
            db.session.commit()
            self.campaign_id = self.campaign.id
            self.token = create_access_token(identity=str(self.user.id))

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_donation(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"campaign_id": self.campaign_id, "amount": 100.5}
        
        response = self.client.post("api/donation/", json=payload, headers=headers)
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.get_data(as_text=True))
        self.assertIn("donation_id", data)
        self.assertEqual(data["msg"], "Donation created")
