from odoo import fields, models


class IntegrationTest(models.Model):
    _name = 'integration.test'
    _description = 'End-to-End Test'
    _order = 'id'

    name = fields.Char(string='Test', required=True)
    test_type = fields.Selection([
        ('whatsapp_send', 'WhatsApp: send from Odoo'),
        ('whatsapp_receive', 'WhatsApp: receive into Odoo'),
        ('mobile_app_check', 'Mobile WhatsApp app still works on same number'),
        ('email_send', 'Email: send from Odoo'),
        ('email_receive', 'Email: receive into Odoo'),
        ('page_message', 'Facebook Page message'),
        ('instagram_message', 'Instagram message'),
        ('failure_path', 'Failure path (invalid/expired token)'),
    ], string='Type', required=True)
    result = fields.Selection([
        ('not_run', 'Not Run'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], string='Result', default='not_run', required=True)
    executed_by = fields.Many2one('res.users', string='Executed By')
    executed_date = fields.Datetime(string='Executed At')
    notes = fields.Text(string='Notes')
