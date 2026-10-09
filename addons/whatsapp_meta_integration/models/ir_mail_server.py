from odoo import fields, models


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    spf_verified = fields.Boolean(
        string='SPF Verified',
        help='Phase 6 checklist: SPF record for the sending domain checked and aligned.')
    dkim_verified = fields.Boolean(
        string='DKIM Verified',
        help='Phase 6 checklist: DKIM signing for the sending domain checked and aligned.')
