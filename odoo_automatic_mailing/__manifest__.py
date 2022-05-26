{
    'name': "Automatic Mailing",
    'summary': """
        Sale Orders and Invoices automatic mailing at Confirmation""",
    'author': "Alliantum",
    'website': "https://www.alliantum.com",
    'category': 'Technical Settings',
    'license': 'AGPL-3',
    'version': '12.0.2.0.3',
    'depends': [
        'sale',
        'account',
        'mail'
        ],
    'data': [
        'security/ir.model.access.csv',
        'data/sale_automatic_template.xml',
        'data/invoice_automatic_template.xml',
        'data/subtype.xml',
        'views/res_partner_form.xml',
        'views/res_users_form.xml',
        'views/automatic_mailing_rule.xml',
        'views/res_config_view.xml',
        'wizards/manage_mailing_rules.xml'
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}
