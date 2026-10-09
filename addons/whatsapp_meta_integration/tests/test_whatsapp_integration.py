from unittest.mock import Mock, patch

from odoo.tests.common import TransactionCase


class TestWhatsAppIntegration(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.write({
            'whatsapp_access_token': 'test-token',
            'whatsapp_verify_token': 'test-verify-token',
            'whatsapp_api_version': 'v21.0',
        })
        cls.portfolio = cls.env['meta.business.portfolio'].create({
            'name': 'Test Portfolio',
            'verification_status': 'verified',
        })
        cls.waba = cls.env['whatsapp.business.account'].create({
            'name': 'Test WABA',
            'waba_id': '111',
            'portfolio_id': cls.portfolio.id,
            'company_id': cls.company.id,
            'cloud_api_status': 'registered',
            'coexistence_eligible': True,
            'coexistence_confirmed': True,
        })
        cls.phone_number = cls.env['whatsapp.phone.number'].create({
            'name': 'Test Line',
            'phone_number': '+15551234567',
            'phone_number_id': '222',
            'waba_id': cls.waba.id,
            'verified': True,
        })
        cls.company.whatsapp_waba_id = cls.waba
        cls.company.whatsapp_phone_number_id = cls.phone_number
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Customer',
            'whatsapp_number': '+15559876543',
        })
        cls.conversation = cls.env['whatsapp.conversation'].create({
            'partner_id': cls.partner.id,
            'phone_number_id': cls.phone_number.id,
        })

    def _mock_response(self, payload, status_code=200):
        response = Mock()
        response.status_code = status_code
        response.json.return_value = payload
        response.text = str(payload)
        return response

    def test_01_send_text_message(self):
        message = self.env['whatsapp.message'].create({
            'conversation_id': self.conversation.id,
            'direction': 'outbound',
            'msg_type': 'text',
            'body': 'Hello from Odoo',
        })
        mock_response = self._mock_response({'messages': [{'id': 'wamid.ABC123'}]})
        with patch('odoo.addons.whatsapp_meta_integration.models.whatsapp_message.requests.post',
                   return_value=mock_response) as mock_post:
            message.action_send()
        self.assertEqual(message.status, 'sent')
        self.assertEqual(message.meta_message_id, 'wamid.ABC123')
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['to'], '15559876543')
        self.assertEqual(kwargs['json']['text']['body'], 'Hello from Odoo')
        self.assertIn('222', mock_post.call_args[0][0])

    def test_02_send_api_error_marks_failed(self):
        message = self.env['whatsapp.message'].create({
            'conversation_id': self.conversation.id,
            'direction': 'outbound',
            'msg_type': 'text',
            'body': 'This will fail',
        })
        mock_response = self._mock_response(
            {'error': {'message': 'Invalid OAuth access token.'}}, status_code=401)
        with patch('odoo.addons.whatsapp_meta_integration.models.whatsapp_message.requests.post',
                   return_value=mock_response):
            result = message.action_send()
        # The failure is recorded on the message (a raised exception would roll
        # back the request transaction and lose the write) and surfaced as a
        # notification action.
        self.assertEqual(message.status, 'failed')
        self.assertIn('Invalid OAuth access token.', message.status_error)
        self.assertEqual(result['tag'], 'display_notification')

    def test_03_inbound_webhook_creates_partner_conversation_message(self):
        payload = {
            'entry': [{
                'id': '111',
                'changes': [{
                    'value': {
                        'messaging_product': 'whatsapp',
                        'contacts': [{'wa_id': '15551110000', 'profile': {'name': 'Webhook Jane'}}],
                        'messages': [{
                            'id': 'wamid.IN1',
                            'from': '15551110000',
                            'type': 'text',
                            'timestamp': '1760000000',
                            'text': {'body': 'Hello from webhook'},
                        }],
                    },
                }],
            }],
        }
        notes = self.env['whatsapp.webhook.log'].process_payload(payload, self.company)
        self.assertTrue(notes)
        partner = self.env['res.partner'].search(
            [('whatsapp_number', '=', '+15551110000')], limit=1)
        self.assertTrue(partner)
        self.assertEqual(partner.name, 'Webhook Jane')
        message = self.env['whatsapp.message'].search(
            [('meta_message_id', '=', 'wamid.IN1')], limit=1)
        self.assertTrue(message)
        self.assertEqual(message.direction, 'inbound')
        self.assertEqual(message.body, 'Hello from webhook')
        self.assertEqual(message.status, 'received')
        self.assertEqual(message.conversation_id.partner_id, partner)

    def test_04_status_update_changes_message_status(self):
        message = self.env['whatsapp.message'].create({
            'conversation_id': self.conversation.id,
            'direction': 'outbound',
            'msg_type': 'text',
            'body': 'Status test',
            'meta_message_id': 'wamid.ST1',
            'status': 'sent',
        })
        payload = {
            'entry': [{
                'id': '111',
                'changes': [{
                    'value': {
                        'messaging_product': 'whatsapp',
                        'statuses': [{
                            'id': 'wamid.ST1',
                            'status': 'read',
                            'timestamp': '1760000100',
                        }],
                    },
                }],
            }],
        }
        self.env['whatsapp.webhook.log'].process_payload(payload, self.company)
        self.assertEqual(message.status, 'read')

    def test_05_webhook_verify_token(self):
        company = self.env['res.company']
        self.assertEqual(
            company.whatsapp_verify_webhook('subscribe', 'test-verify-token', 'challenge-1'),
            self.company)
        self.assertFalse(company.whatsapp_verify_webhook('subscribe', 'wrong-token', 'challenge-1'))
        self.assertFalse(company.whatsapp_verify_webhook('unsubscribe', 'test-verify-token', 'challenge-1'))

    def test_06_conversation_send_message_action(self):
        self.conversation.draft_message = 'Hi there'
        mock_response = self._mock_response({'messages': [{'id': 'wamid.OUT1'}]})
        with patch('odoo.addons.whatsapp_meta_integration.models.whatsapp_message.requests.post',
                   return_value=mock_response):
            action = self.conversation.action_send_message()
        self.assertEqual(action.get('tag'), 'reload')
        message = self.env['whatsapp.message'].search([
            ('conversation_id', '=', self.conversation.id),
            ('direction', '=', 'outbound'),
        ], limit=1, order='id desc')
        self.assertEqual(message.body, 'Hi there')
        self.assertEqual(message.status, 'sent')
        self.assertEqual(message.meta_message_id, 'wamid.OUT1')
        self.assertFalse(self.conversation.draft_message)

    def test_07_find_or_create_partner_by_whatsapp(self):
        partner = self.env['res.partner'].find_or_create_by_whatsapp('+1 (555) 222-3333', 'Sms Sam')
        self.assertEqual(partner.whatsapp_number, '+15552223333')
        again = self.env['res.partner'].find_or_create_by_whatsapp('15552223333')
        self.assertEqual(again, partner)
