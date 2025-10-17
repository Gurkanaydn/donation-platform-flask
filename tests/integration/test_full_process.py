import unittest
from unittest.mock import patch
from app import create_app, db
import json
import hmac
import hashlib
from app.models.donation import Donation
from dotenv import load_dotenv
import os

load_dotenv()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

class FullWorkflowTestCase(unittest.TestCase):
    def setUp(self):
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()

        # DB setup
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def generate_signature(self, payload: dict) -> str:
        raw = json.dumps(payload, indent=4)
        raw_body = raw.encode("utf-8")
        sig = hmac.new(WEBHOOK_SECRET.encode(), raw_body, digestmod=hashlib.sha256).hexdigest()
        return sig
    

    def test_full_workflow(self):
        # Register
        register_payload = {"email": "user@example.com", "password": "123456"}
        resp = self.client.post("/auth/register", json=register_payload)
        self.assertEqual(resp.status_code, 201)

        # Login
        login_payload = {"email": "user@example.com", "password": "123456"}
        resp = self.client.post("/auth/login", json=login_payload)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.get_data(as_text=True))
        access_token = data["access_token"]
        self.assertIsNotNone(access_token)

        headers = {"Authorization": f"Bearer {access_token}"}

        # Create Campaign
        campaign_payload = {
            "title": "Test Campaign",
            "description": "Integration test campaign",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31"
        }
        resp = self.client.post("/api/campaigns/", json=campaign_payload, headers=headers)
        self.assertEqual(resp.status_code, 201)
        campaign_data = json.loads(resp.get_data(as_text=True))
        campaign_id = campaign_data["id"]

        # Create Donation
        donation_payload = {
            "campaign_id": campaign_id,
            "amount": 150.75
        }
        resp = self.client.post("/api/donation/", json=donation_payload, headers=headers)
        self.assertEqual(resp.status_code, 201)
        donation_data = json.loads(resp.get_data(as_text=True))
        self.assertIn("donation_id", donation_data)
        self.assertEqual(donation_data["msg"], "Donation created")
        
        # Trigger Webhook
        webhook_payload = {
            "webhook_id": f"wh_{donation_data["donation_id"]}000",
            "donation_id": donation_data["donation_id"],
            "status": "confirmed"
        }

        signature = self.generate_signature(webhook_payload)
        raw_body = json.dumps(webhook_payload, indent=4).encode("utf8")

        headers = {
            "X-Signature": signature,
            "Content-Type": "application/json"
        }

        resp = self.client.post("/api/donation/webhook", data=raw_body, headers=headers)

        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.get_data(as_text=True))
        self.assertEqual(data["msg"], "Donation confirmed")

        with self.app.app_context():
            donation = db.session.get(Donation, donation_data["donation_id"])
            self.assertEqual(donation.status, "confirmed")
            self.assertEqual(donation.webhook_id, f"wh_{donation_data["donation_id"]}000")

