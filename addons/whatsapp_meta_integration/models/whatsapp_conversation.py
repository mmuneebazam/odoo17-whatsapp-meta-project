from odoo import api, fields, models
from odoo.exceptions import UserError


class WhatsappConversation(models.Model):
    _name = 'whatsapp.conversation'
    _description = 'WhatsApp Conversation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'last_message_date desc, id desc'

    name = fields.Char(string='Conversation', compute='_compute_name', store=True)
    partner_id = fields.Many2one(
        'res.partner', string='Contact', required=True, tracking=True)
    phone_number_id = fields.Many2one(
        'whatsapp.phone.number', string='Phone Number', required=True)
    company_id = fields.Many2one('res.company', related='phone_number_id.company_id', store=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('archived', 'Archived'),
    ], string='Status', default='open', required=True, tracking=True)
    whatsapp_message_ids = fields.One2many(
        'whatsapp.message', 'conversation_id', string='WhatsApp Messages')
    message_count = fields.Integer(string='Message Count', compute='_compute_message_count')
    last_message_date = fields.Datetime(
        string='Last Message', compute='_compute_last_message_date', store=True)
    draft_message = fields.Text(
        string='New Message',
        help='Type a WhatsApp text message and press "Send".')

    @api.depends('partner_id.name', 'phone_number_id.phone_number')
    def _compute_name(self):
        for conversation in self:
            conversation.name = '%s (%s)' % (
                conversation.partner_id.display_name or '?',
                conversation.phone_number_id.phone_number or '?')

    @api.depends('whatsapp_message_ids')
    def _compute_message_count(self):
        for conversation in self:
            conversation.message_count = len(conversation.whatsapp_message_ids)

    @api.depends('whatsapp_message_ids.timestamp')
    def _compute_last_message_date(self):
        for conversation in self:
            conversation.last_message_date = max(
                conversation.whatsapp_message_ids.mapped('timestamp'), default=False)

    def action_send_message(self):
        """Send the draft message of the conversation through the WhatsApp Cloud API."""
        for conversation in self:
            if not conversation.draft_message or not conversation.draft_message.strip():
                raise UserError('Please type a message first.')
            message = self.env['whatsapp.message'].create({
                'conversation_id': conversation.id,
                'direction': 'outbound',
                'msg_type': 'text',
                'body': conversation.draft_message,
            })
            result = message.action_send()
            if result:
                # Send failed: show the error notification, then reload the form.
                result['params']['next'] = {'type': 'ir.actions.client', 'tag': 'reload'}
                return result
            conversation.draft_message = ''
        return {'type': 'ir.actions.client', 'tag': 'reload'}
