from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, socketio, redis_client
from app.models.donation import Donation
from app.models.campaign import Campaign
from app.schemas.donation_schema import DonationCreateSchema, DonationAcceptSchema
from app.models.user import User
from marshmallow import ValidationError
import hmac
import hashlib
from app.utils import connection
import os
from dotenv import load_dotenv

donation_bp = Blueprint("donation", __name__)
load_dotenv()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
donation_create_schema = DonationCreateSchema()
donation_accept_schema = DonationAcceptSchema()


@donation_bp.route("/", methods=["POST"])
@jwt_required()
def create_donation():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        data = donation_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    campaign = Campaign.query.filter_by(id=data["campaign_id"], is_delete=False).first()
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404

    donation = Donation(
        campaign_id=data["campaign_id"],
        user_id=user_id,
        amount=data["amount"],
        status="pending"
    )
    db.session.add(donation)
    user_data = db.session.get(User, user_id)
    
    
    msg = f"{user_data.email} kullanıcısı {data["campaign_id"]} kampanyasına bağış yaptı."
    socketio.emit('new_msg', msg)
    return jsonify({"msg": "Donation created", "donation_id": donation.id}), 201


@donation_bp.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Signature")
    try:
        # JSON body doğrulaması
        data = donation_accept_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    _payload = request.get_data(as_text=True)
    payload = _payload.encode('utf8')
    
    expected_sig = hmac.new(
        key=WEBHOOK_SECRET.encode(),
        msg=payload,  # bytes
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, signature):
        return jsonify({"error": "Invalid signature"}), 400
    
    data = request.get_json()
    webhook_id = data["webhook_id"]
    donation_id = data["donation_id"]

    existing = Donation.query.filter_by(webhook_id=webhook_id).first()
    if existing:
        return jsonify({"msg": "Already processed"}), 200

    donation = db.session.get(Donation, donation_id)

    if not donation:
        return jsonify({"error": "Donation not found"}), 404

    donation.status = "confirmed"
    donation.webhook_id = webhook_id
    user_data = db.session.get(User, donation.user_id)

    db.session.commit()

    connection.enqueue_donation(donation_id, user_data.email)
    
    msg = f"{user_data.email} kullanıcısının kampanya bağışı onaylandı."
    socketio.emit('new_msg', msg)

    redis_client.incrbyfloat(f"campaign:{donation.campaign_id}:total_amount", donation.amount)
    redis_client.incr(f"campaign:{donation.campaign_id}:donor_count")
    all_campaign_keys = redis_client.keys("campaign:*:total_amount")

    campaign_stats = []
    for key in all_campaign_keys:
        cid = key.split(":")[1]
        total_amount = redis_client.get(f"campaign:{cid}:total_amount")
        donor_count = redis_client.get(f"campaign:{cid}:donor_count")

        campaign_stats.append({
            "campaign_id": int(cid),
            "total_amount": float(total_amount or 0),
            "donor_count": int(donor_count or 0)
        })

    socketio.emit(
        "campaigns_update",
        campaign_stats,
    )

    return jsonify({"msg": "Donation confirmed"}), 200