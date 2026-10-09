from odoo import fields, models


class WhatsappBusinessAccount(models.Model):
    _name = 'whatsapp.business.account'
    _description = 'WhatsApp Business Account (WABA)'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    waba_id = fields.Char(
        string='WABA ID', required=True,
        help='WhatsApp Business Account ID from Meta Business Manager.')
    portfolio_id = fields.Many2one('meta.business.portfolio', string='Business Portfolio')
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    cloud_api_status = fields.Selection([
        ('not_registered', 'Not Registered'),
        ('registered', 'Registered for Cloud API'),
        ('verified', 'Verified'),
        ('error', 'Error'),
    ], string='Cloud API Status', default='not_registered', required=True)
    quality_status = fields.Selection([
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('red', 'Red'),
        ('unknown', 'Unknown'),
    ], string='Quality Status', default='unknown')
    phone_number_ids = fields.One2many('whatsapp.phone.number', 'waba_id', string='Phone Numbers')
    coexistence_eligible = fields.Boolean(
        string='Coexistence Eligible (Mobile App + Cloud API)',
        help='Phase 2: confirmed against Meta\'s current documentation that the mobile '
             'WhatsApp Business app and the Cloud API can run on the same number.')
    coexistence_confirmed = fields.Boolean(
        string='Coexistence Confirmed & Signed Off by Client',
        help='Hard constraint of the engagement: the existing mobile WhatsApp Business app '
             'must remain active. Written client sign-off is required before any step that '
             'touches the number\'s registration.')
    coexistence_signoff_date = fields.Date(string='Client Sign-off Date')
    coexistence_notes = fields.Text(
        string='Coexistence Notes',
        help='Document eligibility findings and limitations (e.g. whether messages sent via '
             'Odoo appear in the mobile app history).')
