from odoo import fields, models


class WhatsappPhoneNumber(models.Model):
    _name = 'whatsapp.phone.number'
    _description = 'WhatsApp Phone Number'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    phone_number = fields.Char(
        string='Phone Number (E.164)', required=True,
        help='e.g. +15551234567')
    phone_number_id = fields.Char(
        string='Phone Number ID', required=True,
        help='Meta phone number ID, used in Cloud API calls '
             '(https://graph.facebook.com/<version>/<phone-number-id>/messages).')
    waba_id = fields.Many2one(
        'whatsapp.business.account', string='WhatsApp Business Account',
        required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', related='waba_id.company_id', store=True)
    verified = fields.Boolean(string='Number Verified')
    quality_rating = fields.Selection([
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('red', 'Red'),
        ('unknown', 'Unknown'),
    ], string='Quality Rating', default='unknown')
    connection_status = fields.Selection([
        ('connected', 'Connected'),
        ('pending', 'Pending'),
        ('disconnected', 'Disconnected'),
    ], string='Connection Status', default='pending')
