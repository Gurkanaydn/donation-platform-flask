from marshmallow import Schema, fields

class CampaignSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str()
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    created_by = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class CampaignCreateSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    start_date = fields.Str(required=True)
    end_date = fields.Str(required=True)

class CampaignUpdateSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)