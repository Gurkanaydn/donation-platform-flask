from marshmallow import Schema, fields

class DonationSchema(Schema):
    id = fields.Int()
    campaign_id = fields.Int()
    user_id = fields.Int()
    amount = fields.Float()
    status = fields.Str()
    webhook_id = fields.Str()
    created_at = fields.DateTime()

class DonationCreateSchema(Schema):
    campaign_id = fields.Int(required=True)
    amount = fields.Float(required=True)

class DonationAcceptSchema(Schema):
    status = fields.Str(required=True)
    donation_id = fields.Int(required=True)
    webhook_id = fields.Str(required=True)