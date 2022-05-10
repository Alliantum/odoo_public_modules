from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Partners that are attached to a product, and thus, can purchase it
    restricted_partner_ids = fields.Many2many('res.partner',
                                              string="Customers",
                                              help="If some contacts are attached to the current product,"
                                                   " then this could be just be sold to those customers")
