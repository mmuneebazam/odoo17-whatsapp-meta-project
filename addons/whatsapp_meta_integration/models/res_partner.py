import re

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    whatsapp_number = fields.Char(
        string='WhatsApp Number',
        help='Phone number in E.164 format, e.g. +15551234567')
    whatsapp_conversation_count = fields.Integer(
        string='WhatsApp Conversations', compute='_compute_whatsapp_conversation_count')

    @api.depends('whatsapp_number')
    def _compute_whatsapp_conversation_count(self):
        for partner in self:
            partner.whatsapp_conversation_count = self.env['whatsapp.conversation'].search_count(
                [('partner_id', '=', partner.id)])

    def action_view_whatsapp_conversations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'WhatsApp Conversations',
            'res_model': 'whatsapp.conversation',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    @api.model
    def find_or_create_by_whatsapp(self, phone, name=None):
        """Find a partner by WhatsApp phone number (E.164), creating it if needed."""
        digits = re.sub(r'\D', '', phone or '')
        if not digits:
            return self.env['res.partner']
        e164 = '+%s' % digits
        partner = self.search(
            ['|', '|',
             ('whatsapp_number', '=', e164),
             ('phone', '=', e164),
             ('mobile', '=', e164)], limit=1)
        if not partner:
            partner = self.create({
                'name': name or 'WhatsApp %s' % e164,
                'whatsapp_number': e164,
                'phone': e164,
            })
        elif name and partner.name and partner.name.startswith('WhatsApp +'):
            partner.name = name
        return partner
