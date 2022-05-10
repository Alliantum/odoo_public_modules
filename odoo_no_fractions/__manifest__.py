{
    'name': "Avoid UoM Fractions",
    'summary': """Avoid selling non-integer quantities of a Unit of Measure category""",
    'description': """
    """,
    'author': "Alliantum",
    'website': "https://www.alliantum.com",
    'version': '14.0.0.0.0',
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
