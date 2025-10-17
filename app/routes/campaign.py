from flask import Blueprint, request, jsonify
from app import db, cache
from app.models.campaign import Campaign
from app.schemas.campaign_schema import CampaignSchema, CampaignCreateSchema, CampaignUpdateSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from marshmallow import ValidationError

campaign_bp = Blueprint("campaign", __name__)
campaigns_schema = CampaignSchema()
campaigns_create_schema = CampaignCreateSchema()
campaigns_update_schema = CampaignUpdateSchema()

# Cursor-based pagination
def paginate(query, cursor=None, limit=10):
    if cursor:
        query = query.filter(Campaign.id > int(cursor))
    results = query.order_by(Campaign.id).limit(limit).all()
    next_cursor = results[-1].id if results else None
    return results, next_cursor

@campaign_bp.route("/", methods=["POST"])
@jwt_required()
def create_campaign():
    data = request.get_json()
    try:
        campaigns_create_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    current_user = int(get_jwt_identity())

    title = data.get("title")
    description = data.get("description")
    start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date()
    end_date = datetime.strptime(data.get("end_date"), "%Y-%m-%d").date()

    campaign = Campaign(
        title=title,
        description=description,
        start_date=start_date,
        end_date=end_date,
        created_by=current_user
    )
    db.session.add(campaign)
    db.session.commit()

    return jsonify(campaigns_schema.dump(campaign)), 201


@campaign_bp.route("/", methods=["GET"])
def list_campaigns():
    cursor = request.args.get("cursor")
    limit = int(request.args.get("limit", 10))
    title_filter = request.args.get("title")
    start_filter = request.args.get("start_date")
    end_filter = request.args.get("end_date")
    campaigns_schema = CampaignSchema(many=True)
    
    query = Campaign.query.filter_by(is_delete=False)
    
    # 🔹 Filtreler
    if title_filter:
        query = query.filter(Campaign.title.ilike(f"%{title_filter}%"))
    if start_filter:
        try:
            start_date = datetime.strptime(start_filter, "%Y-%m-%d").date()
            query = query.filter(Campaign.start_date >= start_date)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
    if end_filter:
        try:
            end_date = datetime.strptime(end_filter, "%Y-%m-%d").date()
            query = query.filter(Campaign.end_date <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400

    # 🔹 Pagination
    campaigns, next_cursor = paginate(query, cursor, limit)

    return jsonify({
        "campaigns": campaigns_schema.dump(campaigns),
        "next_cursor": next_cursor
    }), 200

@campaign_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_campaign(id):
    data = request.get_json()

    try:
        data = campaigns_update_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    campaign = Campaign.query.filter_by(id=id, is_delete=False).first()
    if not campaign:
        return jsonify({"error": f"Campaign with id {id} not found"}), 404

    if "title" in data: campaign.title = data["title"]
    if "description" in data: campaign.description = data["description"]
    if "start_date" in data: campaign.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
    if "end_date" in data: campaign.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

    db.session.commit()

    
    cache_key = f"campaign_id:{id}"
    cached = cache.get(cache_key)
    # cache'deki datayı update et ya da sil.
    if cached:
        cache.set(cache_key, campaigns_schema.dump(campaign))
    
    return jsonify(campaigns_schema.dump(campaign))


@campaign_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_campaign(id):
    campaign = Campaign.query.filter_by(id=id, is_delete=False).first()
    if not campaign:
        return jsonify({"error": f"Campaign with id {id} not found"}), 404
    
    campaign.is_delete = True
    db.session.commit()


    cache_key = f"campaign_id:{id}"
    cached = cache.get(cache_key)

    if cached:
        cache.delete(cache_key)
    return jsonify({"msg": "Campaign deleted successfully"}), 200


@campaign_bp.route("/<int:id>", methods=["GET"])
def get_campaign(id):
    cache_key = f"campaign_id:{id}"
    cached = cache.get(cache_key)
    if cached:
        return jsonify({"from_cached": True, "data": cached})


    campaign = Campaign.query.filter_by(id=id, is_delete=False).first()
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404
    

    cache.set(cache_key, campaigns_schema.dump(campaign))
    return jsonify({"from_cached": False, "data": campaigns_schema.dump(campaign)})