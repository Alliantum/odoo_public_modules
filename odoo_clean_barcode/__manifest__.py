# -*- coding: utf-8 -*-
{
    'name': "Alliantum Clean Barcode",

    'summary': """
        Generates a svg vector image of a barcode in order to embed it into a pdf""",

    'description': """
        For more information please take a look at this link:
        https://github.com/Alliantum/odoo_clean_barcode/blob/master/README.md
    """,
    'author': "Alliantum",
    'website': "https://www.alliantum.com/",
    'category': 'Uncategorized',
    'license': 'AGPL-3',
    'version': '14.0.1.0.2',
    'depends': [
        'base'
    ],
    'pre_init_hook': 'version_check' # checks reportlab version. Ensure you have pip install reportlab==3.5.49 previously
}
