from odoo import fields, models


class MetaInstagramAccount(models.Model):
    _name = 'meta.instagram.account'
    _description = 'Instagram Business Account'
    _order = 'name'

    name = fields.Char(string='Account Name', required=True)
    instagram_id = fields.Char(string='Instagram Account ID', required=True)
    account_type = fields.Selection([
        ('personal', 'Personal'),
        ('creator', 'Creator'),
        ('business', 'Business'),
        ('professional', 'Professional (linked to business)'),
    ], string='Account Type', default='business', required=True,
        help='Phase 0/4: only a genuine Instagram Business/Professional account can be '
             'linked to a Page and used for API-based messaging.')
    portfolio_id = fields.Many2one('meta.business.portfolio', string='Business Portfolio')
    page_id = fields.Many2one('meta.page', string='Linked Facebook Page')
    linked_ok = fields.Boolean(string='Correctly Linked (Page + Portfolio)')
    messaging_permission = fields.Selection([
        ('missing', 'Missing'),
        ('requested', 'Requested'),
        ('granted', 'Granted'),
    ], string='Instagram Messaging Permission', default='missing')
