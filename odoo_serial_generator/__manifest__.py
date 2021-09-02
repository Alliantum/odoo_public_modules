# -*- coding: utf-8 -*-
{
    'name': "Generate Serial Numbers",
    'summary': """Automatic generation of Serial Numbers on transfers""",
    'author': "Alliantum",
    'website': "https://www.alliantum.com",
    'version': '12.0.1.0.0',
    'license': 'LGPL-3',
    'category': 'Warehouse',
    'depends': ['stock'],
    'data': [
        'views/stock_views.xml',
        'wizards/stock_assign_serial_views.xml',
    ]
}
