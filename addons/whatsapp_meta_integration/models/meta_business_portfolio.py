from odoo import fields, models


class MetaBusinessPortfolio(models.Model):
    _name = 'meta.business.portfolio'
    _description = 'Meta Business Portfolio (Business Manager)'
    _order = 'name'

    name = fields.Char(string='Portfolio Name', required=True)
    business_id = fields.Char(string='Business ID')
    verification_status = fields.Selection([
        ('unverified', 'Unverified'),
        ('pending', 'Verification Pending'),
        ('under_review', 'Under Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ], string='Business Verification Status', default='unverified', required=True,
        help='Phase 1: resolve any pending or failed Meta Business verification first - '
             'most downstream WhatsApp/Page/Instagram permission issues cannot be fully '
             'resolved while business verification is incomplete.')
    verification_date = fields.Date(string='Verification Date')
    owner_id = fields.Many2one(
        'res.partner', string='Business Owner',
        help='The client must hold primary admin ownership of the portfolio, the Page, '
             'the Instagram account and the WABA - not a third party or previous agency.')
    admin_user_ids = fields.Many2many('res.users', string='Admin Users')
    page_ids = fields.One2many('meta.page', 'portfolio_id', string='Facebook Pages')
    instagram_ids = fields.One2many('meta.instagram.account', 'portfolio_id', string='Instagram Accounts')
    waba_ids = fields.One2many('whatsapp.business.account', 'portfolio_id', string='WhatsApp Business Accounts')
    asset_count = fields.Integer(string='Assigned Assets', compute='_compute_asset_count')
    notes = fields.Text(string='Notes')

    def _compute_asset_count(self):
        for portfolio in self:
            portfolio.asset_count = (
                len(portfolio.page_ids) + len(portfolio.instagram_ids) + len(portfolio.waba_ids))
