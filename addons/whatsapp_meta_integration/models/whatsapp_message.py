import logging
import re

import requests

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WhatsappMessage(models.Model):
    _name = 'whatsapp.message'
    _description = 'WhatsApp Message'
    _order = 'timestamp desc, id desc'

    conversation_id = fields.Many2one(
        'whatsapp.conversation', string='Conversation', required=True, ondelete='cascade')
    partner_id = fields.Many2one(
        'res.partner', string='Contact', related='conversation_id.partner_id', store=True)
    company_id = fields.Many2one(
        'res.company', related='conversation_id.company_id', store=True)
    direction = fields.Selection([
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ], string='Direction', required=True, default='outbound')
    msg_type = fields.Selection([
        ('text', 'Text'),
        ('template', 'Template'),
        ('image', 'Image'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('location', 'Location'),
        ('unsupported', 'Unsupported'),
    ], string='Type', default='text', required=True)
    body = fields.Text(string='Message Body')
    template_id = fields.Many2one('whatsapp.template', string='Template')
    meta_message_id = fields.Char(
        string='Meta Message ID (wamid)', index=True,
        help='Message ID returned by the Meta Cloud API; used to match status callbacks.')
    status = fields.Selection([
        ('received', 'Received'),
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ], string='Status', default='pending', required=True)
    status_error = fields.Text(string='Last Error')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)

    def action_send(self):
        """Send pending/failed outbound messages through the WhatsApp Cloud API.

        Returns a ``display_notification`` client action if any message failed
        (the failure is recorded on the message first, so it must not be raised:
        an exception would roll back the request transaction and lose the write),
        otherwise returns None.
        """
        errors = []
        for message in self:
            if message.direction != 'outbound':
                raise UserError('Only outbound messages can be sent.')
            if message.status not in ('pending', 'failed'):
                raise UserError('This message was already sent.')
            error = message._send_via_api()
            if error:
                errors.append(error)
        if errors:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'WhatsApp send failed',
                    'message': '\n'.join(errors),
                    'type': 'danger',
                    'sticky': True,
                },
            }
        return None

    def _send_via_api(self):
        """Send this message via the Cloud API.

        Returns False on success, or the error message on failure (the message
        is marked as failed before returning, so the status survives the request).
        """
        self.ensure_one()
        company = self.company_id or self.env.company
        phone_number = self.conversation_id.phone_number_id
        if not phone_number.phone_number_id:
            raise UserError(
                'The WhatsApp phone number is not fully configured '
                '(missing the Meta Phone Number ID).')
        if not company.whatsapp_access_token:
            raise UserError(
                'No WhatsApp access token configured. Set it in '
                'Settings > General Settings > WhatsApp / Meta Integration.')
        recipient = self._get_recipient_digits()
        if not recipient:
            raise UserError('The contact has no phone number to send WhatsApp messages to.')
        api_version = company.whatsapp_api_version or 'v21.0'
        url = 'https://graph.facebook.com/%s/%s/messages' % (api_version, phone_number.phone_number_id)
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': recipient,
        }
        if self.msg_type == 'template':
            if not self.template_id:
                raise UserError('Please select a template to send.')
            payload['type'] = 'template'
            payload['template'] = {
                'name': self.template_id.template_name,
                'language': {'code': self.template_id.language_code},
            }
        else:
            payload['type'] = 'text'
            payload['text'] = {'body': self.body or ''}
        try:
            response = requests.post(
                url, json=payload,
                headers={
                    'Authorization': 'Bearer %s' % company.whatsapp_access_token,
                    'Content-Type': 'application/json',
                },
                timeout=30)
            data = response.json()
        except Exception as error:
            self._mark_failed('API request failed: %s' % error)
            return 'API request failed: %s' % error
        if response.status_code == 200 and data.get('messages'):
            self.write({
                'meta_message_id': data['messages'][0].get('id'),
                'status': 'sent',
                'status_error': False,
            })
            return False
        error_message = (
            (data.get('error') or {}).get('message')
            or response.text
            or 'HTTP %s' % response.status_code
        )
        self._mark_failed(error_message)
        return error_message

    def _mark_failed(self, error_message):
        self.write({'status': 'failed', 'status_error': error_message})
        _logger.warning('WhatsApp message %s failed: %s', self.id, error_message)

    def _get_recipient_digits(self):
        partner = self.partner_id
        raw = partner.whatsapp_number or partner.phone or partner.mobile or ''
        return re.sub(r'\D', '', raw) or False
