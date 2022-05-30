# -*- coding: utf-8 -*-
{
    'name': "SO Warning State",
    'summary': """Adds a Warning state to Sale's Orders""",
    'description': """
         - Implement some logic to catch the attention of salesman when all the deliveries for a sale order has been
         cancelled.
         - Form view show delivery count button in warning background color.
         - Tree view show status 'warning' lines in warning background color.
    """,
    'author': "Alliantum",
    'website': "https://www.alliantum.com",
    'version': '13.0.1.0.2',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': ['base', 'sale', 'sale_stock'],
    'data': [
        'views/sale_order_view.xml',
    ],
}
