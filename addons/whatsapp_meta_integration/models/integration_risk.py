from odoo import fields, models


class IntegrationRisk(models.Model):
    _name = 'integration.risk'
    _description = 'Risk Register Entry'
    _order = 'id'

    name = fields.Char(string='Risk', required=True)
    description = fields.Text(string='Why It Matters')
    mitigation = fields.Text(string='Mitigation')
    likelihood = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Likelihood', default='medium')
    impact = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Impact', default='medium')
    status = fields.Selection([
        ('open', 'Open'),
        ('mitigated', 'Mitigated'),
        ('closed', 'Closed'),
    ], string='Status', default='open')
    owner_id = fields.Many2one('res.users', string='Owner')
