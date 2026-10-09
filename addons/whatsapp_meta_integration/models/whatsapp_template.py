from odoo import fields, models


class WhatsappTemplate(models.Model):
    _name = 'whatsapp.template'
    _description = 'WhatsApp Message Template'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    template_name = fields.Char(
        string='Meta Template Name', required=True,
        help='Exact template name as approved in Meta Business Manager '
             '(lowercase with underscores, e.g. order_confirmation).')
    language_code = fields.Char(
        string='Language Code', default='en_US', required=True,
        help='e.g. en_US, es_MX, ur_PK')
    category = fields.Selection([
        ('marketing', 'Marketing'),
        ('utility', 'Utility'),
        ('authentication', 'Authentication'),
    ], string='Category', default='utility', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Approval Status', default='draft', required=True,
        help='Phase 3: confirm at least one template is approved and sends correctly '
             'end to end from Odoo.')
    body = fields.Text(
        string='Template Body',
        help='Use {{1}}, {{2}}, ... for variable placeholders.')
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
