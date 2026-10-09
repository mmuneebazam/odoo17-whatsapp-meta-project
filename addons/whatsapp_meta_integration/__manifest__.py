{
    'name': 'WhatsApp & Meta Integration',
    'version': '17.0.1.0.0',
    'category': 'Discuss',
    'summary': 'WhatsApp Business Platform (Cloud API) + Meta Business Manager integration with delivery-plan tracking',
    'description': """
WhatsApp & Meta Integration for Odoo 17
=======================================

Implements the "Odoo WhatsApp & Meta Integration - Connect, Verify & Fix" delivery plan
as a working Odoo 17 custom module (the plan targets Odoo 19; Odoo 17 has no native
WhatsApp app, so this module builds the integration from scratch on the Meta Cloud API).

Features
--------
* WhatsApp Business Platform (Cloud API): send/receive WhatsApp messages inside Odoo,
  linked to contacts, with a public webhook controller (verify token + inbound payloads)
  and message status tracking (sent / delivered / read / failed).
* Mobile-app coexistence tracking: the plan's hard constraint (keep the mobile WhatsApp
  Business app active on the same number) is modelled as explicit, auditable fields.
* Meta Business Manager audit models: Business Portfolio (verification status,
  ownership, admins), Facebook Page, Instagram Business account and their links.
* Permissions & tokens: permission inventory with minimal-scope review, Meta App
  Review tracking, and a long-lived System User token strategy with expiry date.
* Email integration: SPF/DKIM deliverability check fields on outgoing mail servers.
* Delivery plan tracking loaded from the project plan: Phases 0-8 with indicative
  hours, Deliverables checklist, Definition of Done, Risk Register, End-to-End test
  log and a Maintenance schedule.
""",
    'author': 'Arena.ai Agent Mode',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/ir_mail_server_views.xml',
        'views/res_config_settings_views.xml',
        'views/meta_business_portfolio_views.xml',
        'views/whatsapp_business_account_views.xml',
        'views/whatsapp_phone_number_views.xml',
        'views/meta_page_views.xml',
        'views/meta_instagram_account_views.xml',
        'views/whatsapp_template_views.xml',
        'views/whatsapp_conversation_views.xml',
        'views/whatsapp_message_views.xml',
        'views/meta_permission_grant_views.xml',
        'views/meta_app_review_views.xml',
        'views/whatsapp_webhook_log_views.xml',
        'views/integration_phase_views.xml',
        'views/integration_deliverable_views.xml',
        'views/integration_dod_views.xml',
        'views/integration_risk_views.xml',
        'views/integration_test_views.xml',
        'views/integration_maintenance_views.xml',
        'views/menu_views.xml',
        'data/integration_phases.xml',
        'data/integration_deliverables.xml',
        'data/integration_dods.xml',
        'data/integration_risks.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,
}
