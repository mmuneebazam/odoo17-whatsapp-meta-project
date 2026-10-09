from odoo import fields, models


class MetaPage(models.Model):
    _name = 'meta.page'
    _description = 'Facebook Page'
    _order = 'name'

    name = fields.Char(string='Page Name', required=True)
    page_id = fields.Char(string='Page ID', required=True)
    portfolio_id = fields.Many2one('meta.business.portfolio', string='Business Portfolio')
    instagram_id = fields.Many2one('meta.instagram.account', string='Linked Instagram Account')
    linked_ok = fields.Boolean(
        string='Correctly Linked (Portfolio + Instagram)',
        help='Phase 4: the Page is assigned to the correct Business Portfolio and linked '
             'to the correct Instagram Business account.')
    messaging_permission = fields.Selection([
        ('missing', 'Missing'),
        ('requested', 'Requested'),
        ('granted', 'Granted'),
    ], string='Page Messaging Permission', default='missing')
    admin_notes = fields.Text(
        string='Admin / Roles Notes',
        help='Record who holds admin/editor roles on the Page.')
