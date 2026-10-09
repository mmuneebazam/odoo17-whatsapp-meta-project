import json
import logging
from datetime import datetime

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class WhatsappWebhookLog(models.Model):
    _name = 'whatsapp.webhook.log'
    _description = 'WhatsApp Webhook Log'
    _order = 'create_date desc'

    company_id = fields.Many2one('res.company', string='Company')
    event_type = fields.Selection([
        ('inbound_message', 'Inbound Message'),
        ('status_update', 'Status Update'),
        ('verification', 'Verification'),
        ('unknown', 'Unknown'),
    ], string='Event Type', default='unknown', required=True)
    payload = fields.Text(string='Payload')
    result = fields.Text(string='Result')

    @api.model
    def log_event(self, company, event_type, payload, result):
        if isinstance(payload, (dict, list)):
            payload_text = json.dumps(payload, indent=2, default=str)
        else:
            payload_text = str(payload)
        if isinstance(result, (list, tuple)):
            result_text = ', '.join(str(item) for item in result)
        else:
            result_text = str(result)
        return self.create({
            'company_id': company.id if company else False,
            'event_type': event_type,
            'payload': payload_text[:100000],
            'result': result_text[:10000],
        })

    @api.model
    def process_payload(self, payload, company):
        """Process a Meta webhook payload; returns a list of processing notes."""
        notes = []
        for entry in payload.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value') or {}
                messaging_product = value.get('messaging_product')
                if messaging_product and messaging_product != 'whatsapp':
                    continue
                contacts = {
                    contact.get('wa_id'): (contact.get('profile') or {}).get('name')
                    for contact in value.get('contacts', [])
                }
                for message in value.get('messages', []):
                    self._process_inbound_message(message, contacts, company)
                    notes.append('inbound message %s' % message.get('id'))
                for status in value.get('statuses', []):
                    self._process_status(status)
                    notes.append('status %s -> %s' % (status.get('id'), status.get('status')))
        return notes

    def _process_inbound_message(self, message, contacts, company):
        phone_number = company.whatsapp_phone_number_id
        partner = self.env['res.partner'].sudo().find_or_create_by_whatsapp(
            message.get('from'), contacts.get(message.get('from')))
        if not partner:
            _logger.warning('Inbound WhatsApp message %s dropped: no sender number.', message.get('id'))
            return
        conversation = self.env['whatsapp.conversation'].sudo().search([
            ('partner_id', '=', partner.id),
            ('phone_number_id', '=', phone_number.id),
        ], limit=1) if phone_number else self.env['whatsapp.conversation']
        if not conversation:
            if not phone_number:
                _logger.warning(
                    'Inbound WhatsApp message %s dropped: no phone number configured for company %s.',
                    message.get('id'), company.display_name)
                return
            conversation = self.env['whatsapp.conversation'].sudo().create({
                'partner_id': partner.id,
                'phone_number_id': phone_number.id,
            })
        msg_type = message.get('type') or 'text'
        if msg_type not in ('text', 'template', 'image', 'document', 'audio', 'video', 'location'):
            msg_type = 'unsupported'
        if msg_type == 'text':
            body = (message.get('text') or {}).get('body') or ''
        elif msg_type == 'template':
            template = message.get('template') or {}
            body = '[Template: %s]' % template.get('name', '')
        else:
            body = '[%s message]' % msg_type
        timestamp = (
            datetime.fromtimestamp(int(message['timestamp']))
            if message.get('timestamp') else fields.Datetime.now())
        self.env['whatsapp.message'].sudo().create({
            'conversation_id': conversation.id,
            'direction': 'inbound',
            'msg_type': msg_type,
            'body': body,
            'meta_message_id': message.get('id'),
            'status': 'received',
            'timestamp': timestamp,
        })

    def _process_status(self, status):
        message = self.env['whatsapp.message'].sudo().search(
            [('meta_message_id', '=', status.get('id'))], limit=1)
        if not message:
            _logger.info('Status update for unknown WhatsApp message %s', status.get('id'))
            return
        new_status = status.get('status')
        if new_status not in ('sent', 'delivered', 'read', 'failed'):
            return
        vals = {'status': new_status}
        if new_status == 'failed':
            errors = status.get('errors') or []
            vals['status_error'] = errors[0].get('message') if errors else 'Unknown WhatsApp error'
        if status.get('timestamp'):
            vals['timestamp'] = datetime.fromtimestamp(int(status['timestamp']))
        message.write(vals)
