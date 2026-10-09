import json
import logging

from odoo.http import Controller, request, route

_logger = logging.getLogger(__name__)


class WhatsAppWebhookController(Controller):
    """Public webhook endpoint used by Meta (WhatsApp Business Platform).

    GET  /whatsapp/webhook  -> webhook verification handshake (hub.mode / hub.verify_token / hub.challenge)
    POST /whatsapp/webhook  -> inbound messages and message status updates

    Meta POSTs a raw JSON body (not a JSON-RPC envelope), so the POST route is
    type='http' and the body is parsed manually.
    """

    @route('/whatsapp/webhook', type='http', auth='public', methods=['GET'], csrf=False)
    def webhook_verify(self, **kwargs):
        company = request.env['res.company'].sudo().whatsapp_verify_webhook(
            kwargs.get('hub.mode'), kwargs.get('hub.verify_token'), kwargs.get('hub.challenge'))
        if company:
            _logger.info('WhatsApp webhook verified for company %s', company.display_name)
            return request.make_response(kwargs.get('hub.challenge') or '', status=200)
        _logger.warning('WhatsApp webhook verification failed: %s', kwargs)
        return request.make_response('Verification failed', status=403)

    @route('/whatsapp/webhook', type='http', auth='public', methods=['POST'], csrf=False)
    def webhook_inbound(self):
        payload = request.httprequest.get_json(force=True, silent=True) or {}
        company = request.env['res.company'].sudo().whatsapp_find_company_for_webhook(payload)
        if not company:
            _logger.warning('WhatsApp webhook payload received but no company is configured.')
            return request.make_response(
                json.dumps({'error': 'No company configured for the WhatsApp webhook'}),
                headers=[('Content-Type', 'application/json')], status=200)
        notes = request.env['whatsapp.webhook.log'].sudo().process_payload(payload, company)
        request.env['whatsapp.webhook.log'].sudo().log_event(company, 'inbound_message', payload, notes)
        return request.make_response(
            json.dumps({'status': 'ok', 'processed': notes}),
            headers=[('Content-Type', 'application/json')], status=200)
