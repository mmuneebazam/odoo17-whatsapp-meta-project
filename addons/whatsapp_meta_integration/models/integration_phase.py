from odoo import fields, models


class IntegrationPhase(models.Model):
    _name = 'integration.phase'
    _description = 'Delivery Plan Phase'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    code = fields.Char(string='Phase', required=True, help='e.g. 0, 1, 2 ...')
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Scope')
    expected_output = fields.Text(string='Expected Output')
    status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ], string='Status', default='not_started', required=True)
    hours_planned_min = fields.Float(string='Planned Hours (Min)')
    hours_planned_max = fields.Float(string='Planned Hours (Max)')
    hours_spent = fields.Float(string='Hours Spent')
