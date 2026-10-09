import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    whatsapp_waba_id = fields.Many2one(
        'whatsapp.business.account', string='WhatsApp Business Account (WABA)',
        help='The WhatsApp Business Account connected to this company.')
    whatsapp_phone_number_id = fields.Many2one(
        'whatsapp.phone.number', string='WhatsApp Phone Number',
        domain="[('waba_id', '=', whatsapp_waba_id)]",
        help='The phone number used to send and receive WhatsApp messages.')
    whatsapp_access_token = fields.Char(
        string='Access Token (System User)',
        help='Long-lived System User access token from Meta Business Manager. '
             'Never use a short-lived user token for a server-side integration.')
    whatsapp_app_secret = fields.Char(
        string='App Secret',
        help='Meta app secret, used to verify webhook payload signatures (X-Hub-Signature-256).')
    whatsapp_verify_token = fields.Char(
        string='Webhook Verify Token',
        help='A random string you define here; it must match the "Verify Token" entered in the '
             'Meta App webhook configuration.')
    whatsapp_api_version = fields.Char(string='Graph API Version', default='v21.0')
    whatsapp_token_expiry_date = fields.Date(
        string='Access Token Expiry / Renewal Date',
        help='System User tokens can expire or be revoked; record the renewal date here.')
    whatsapp_webhook_url = fields.Char(
        string='Webhook URL', compute='_compute_whatsapp_webhook_url',
        help='Callback URL to configure in the Meta App webhook settings.')

    @api.depends('whatsapp_verify_token')
    def _compute_whatsapp_webhook_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
        for company in self:
            company.whatsapp_webhook_url = '%s/whatsapp/webhook' % base_url if base_url else ''

    @api.model
    def whatsapp_verify_webhook(self, hub_mode, verify_token, challenge):
        """Return the company whose verify token matches the Meta handshake, else empty."""
        if hub_mode != 'subscribe' or not verify_token or not challenge:
            return self.browse()
        return self.search([('whatsapp_verify_token', '=', verify_token)], limit=1)

    @api.model
    def whatsapp_find_company_for_webhook(self, payload):
        """Find the company an inbound webhook payload belongs to (matched on WABA id)."""
        waba_ids = [entry.get('id') for entry in payload.get('entry', []) if entry.get('id')]
        if waba_ids:
            company = self.search([('whatsapp_waba_id.waba_id', 'in', waba_ids)], limit=1)
            if company:
                return company
        return self.search([('whatsapp_access_token', '!=', False)], limit=1)
