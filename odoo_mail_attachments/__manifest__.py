# -*- coding: utf-8 -*-
{
    'name': "Mails Dynamic Attachments",
    'summary': """
        Attach Dynamically Generated Documents to your Mails""",
    'description': """
    """,
    'author': "Alliantum",
    'website': "https://www.alliantum.com",
    'license': 'AGPL-3',
    'version': '14.0.1.0.2',
    'category': 'Technical',
    'depends': [
        'base_setup'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/manage_mail_attachments.xml',
        'views/mail_attachment_line.xml',
        'views/res_config_settings.xml'
    ],
    'auto_install': False,
    'application': False,
    'installable': True
}
