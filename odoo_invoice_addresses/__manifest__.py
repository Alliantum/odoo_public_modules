# -*- coding: utf-8 -*-
{
    'name': "Invoice Addresses",
    'summary': """
        Set Different Invoice Addresses under the same Company
        """,
    'description': """
        In order to give the ability to have different Invoice address and Delivery address this module adds two new fields to all the invoices.
    """,
    'author': "Alliantum",

    'website': "http://www.alliantum.com",

    'category': 'Uncategorized',

    'license': 'AGPL-3',

    'version': '14.0.1.0.1',

    'depends': ['base', 'account', 'sale'],

    'data': [
        'views/account_invoice_view.xml',
        'reports/invoice_template.xml',
    ],
}
