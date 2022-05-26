{
    'name': "Extended Barcodes",
    'summary': "Allows to generate a whole new range of barcodes types.",
    'author': "Alliantum",
    'website': "https://www.alliantum.com",
    'license': 'AGPL-3',
    'version': '12.0.1.0.2',
    'category': 'Technical',
    'depends': [
        'web',
    ],
    'data': [
        'data/barcodes_extended_libraries.xml'
    ],
    'application': False,
    'external_dependencies': {
        'python': ['pyzint'],  # pip install pyzint
    },
}
