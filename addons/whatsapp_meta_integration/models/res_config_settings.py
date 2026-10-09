from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_waba_id = fields.Many2one(related='company_id.whatsapp_waba_id', readonly=False)
    whatsapp_phone_number_id = fields.Many2one(
        related='company_id.whatsapp_phone_number_id', readonly=False,
        domain="[('waba_id', '=', whatsapp_waba_id)]")
    whatsapp_access_token = fields.Char(related='company_id.whatsapp_access_token', readonly=False)
    whatsapp_app_secret = fields.Char(related='company_id.whatsapp_app_secret', readonly=False)
    whatsapp_verify_token = fields.Char(related='company_id.whatsapp_verify_token', readonly=False)
    whatsapp_api_version = fields.Char(related='company_id.whatsapp_api_version', readonly=False)
    whatsapp_token_expiry_date = fields.Date(related='company_id.whatsapp_token_expiry_date', readonly=False)
    whatsapp_webhook_url = fields.Char(related='company_id.whatsapp_webhook_url', readonly=True)
