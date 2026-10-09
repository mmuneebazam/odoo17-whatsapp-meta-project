from odoo import fields, models


class MetaPermissionGrant(models.Model):
    _name = 'meta.permission.grant'
    _description = 'Meta App / System User Permission'
    _order = 'name'

    name = fields.Char(
        string='Permission', required=True,
        help='e.g. whatsapp_business_messaging, whatsapp_business_management, '
             'pages_messaging, instagram_manage_messages, business_management')
    app_name = fields.Char(
        string='Meta App / System User',
        help='The Meta app or System User this permission is granted to.')
    scope = fields.Selection([
        ('required', 'Required for this integration'),
        ('optional', 'Optional'),
        ('granted_but_unused', 'Granted but not used (remove)'),
    ], string='Scope', default='required', required=True,
        help='Phase 5: keep exactly the access needed; remove anything broader than '
             'what the Odoo integration actually uses.')
    status = fields.Selection([
        ('missing', 'Missing'),
        ('requested', 'Requested'),
        ('granted', 'Granted'),
        ('revoked', 'Revoked'),
    ], string='Status', default='missing', required=True)
    notes = fields.Text(string='Notes')
