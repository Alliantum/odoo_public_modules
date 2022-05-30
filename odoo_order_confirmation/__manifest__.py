# -*- coding: utf-8 -*-
{
    'name': "Block SO on Big Quantities",
    'summary': """Block a SO until Stock Mangers allow it depending on maximum amounts (configurable)""",
    'description': """
    """,
    'author': "Alliantum",
    'website': "https://www.alliantum.com",
    'version': '13.0.1.0.2',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'base',
        'account',
        'analytic',
        'product',
        'uom',
        'sale_stock',
        'sale',
        'sale_management',
        'sales_team',
        'stock',
        'mail',
        'delivery',
        'purchase_stock'
    ],
    'data': [
        'security/sales_stock_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_view.xml',
        'views/sale.xml',
    ],
}
