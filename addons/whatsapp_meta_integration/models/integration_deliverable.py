from odoo import fields, models


class IntegrationDeliverable(models.Model):
    _name = 'integration.deliverable'
    _description = 'Deliverables Checklist Item'
    _order = 'id'

    name = fields.Char(string='Deliverable', required=True)
    phase_id = fields.Many2one('integration.phase', string='Phase', ondelete='set null')
    done = fields.Boolean(string='Delivered')
    notes = fields.Text(string='Notes')
