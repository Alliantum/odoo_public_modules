# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

# Here we just add the field on the product variant
class ProductProduct(models.Model):
    _inherit = 'product.product'

    max_production = fields.Float("Maximum per MO", help="Maximum amount allowed for a single MO for this product,"
                                                         " calculated with the default UoM of the product.")
