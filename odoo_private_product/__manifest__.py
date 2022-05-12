{
    'name': "Brand Partner Products",
    'summary': """Restricted (private) products for Customers""",
    'description': """
        Create a relation between a product and a customer, and avoid selling that products to any other customer.
    """,
    'author': "Alliantum",
    'website': "https://www.alliantum.com",
    'version': '13.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Inventory',
    'depends': ['base', 'product', 'sale'],
    'data': [
        'views/product_template.xml',
        'views/product_variant_view.xml',
        'views/res_partner.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}
