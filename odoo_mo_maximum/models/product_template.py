# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

# Creation of maximum field on product template
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    max_production = fields.Float("Maximum per MO", help="Maximum amount allowed for a single MO for this product,"
                                                         " calculated with the default UoM of the product.",
                                  compute="_get_max_production", inverse='_set_max_production')
    def _get_max_production(self):
        # If there is only one variant set the variant value
        for template in self:
            if template.product_variant_count == 1:
                template.max_production = template.product_variant_id.max_production
            else:
                template.max_production = False
    def _set_max_production(self):
        # When max_production is set it changes it's variant (if there is only one)
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.max_production = self.max_production
