{
    'name': "Avoid UoM Fractions",
    'summary': """Avoid selling non-integer quantities of a Unit of Measure category""",
    'description': """
    """,
    'author': "Alliantum",
    'website': "https://www.alliantum.com",
    'version': '12.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'depends': ['uom', 'sale', 'account'],
    'data': [
        'views/product_uom_categ.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}
