from odoo import fields, models


class IntegrationDod(models.Model):
    _name = 'integration.dod'
    _description = 'Definition of Done Item'
    _order = 'id'

    name = fields.Char(string='Criterion', required=True)
    done = fields.Boolean(string='Met')
    verified_by = fields.Many2one('res.users', string='Verified By')
    verification_date = fields.Date(string='Verification Date')
    notes = fields.Text(string='Notes')
