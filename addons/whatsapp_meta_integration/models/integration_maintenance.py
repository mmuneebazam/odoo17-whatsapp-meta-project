from odoo import fields, models


class IntegrationMaintenance(models.Model):
    _name = 'integration.maintenance'
    _description = 'Maintenance Schedule Item'
    _order = 'next_due, id'

    name = fields.Char(string='Item', required=True)
    frequency = fields.Selection([
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half-Yearly'),
        ('yearly', 'Yearly'),
        ('on_change', 'On Change'),
    ], string='Frequency', required=True, default='yearly')
    next_due = fields.Date(string='Next Due')
    owner_id = fields.Many2one('res.users', string='Owner')
    notes = fields.Text(
        string='Notes',
        help='Phase 8: what needs periodic attention (token renewal, business verification '
             'renewal, template re-approval if content changes) and roughly how often.')
