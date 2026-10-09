from odoo import fields, models


class MetaAppReview(models.Model):
    _name = 'meta.app.review'
    _description = 'Meta App Review'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    status = fields.Selection([
        ('not_required', 'Not Required'),
        ('preparing', 'Preparing'),
        ('submitted', 'Submitted'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='not_required', required=True,
        help='Phase 5: if any permission requires Meta App Review, request only the '
             'permissions genuinely required for this scope - never broad permissions '
             '"just in case".')
    permissions_requested = fields.Text(
        string='Permissions Requested',
        help='Minimum permission set required for this scope.')
    use_case_description = fields.Text(string='Use Case Description')
    submitted_date = fields.Date(string='Submitted On')
    result_notes = fields.Text(string='Result Notes')
