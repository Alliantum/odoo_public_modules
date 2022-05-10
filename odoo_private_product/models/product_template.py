from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Partners that are attached to a product, and thus, can purchase it
    restricted_partner_ids = fields.Many2many('res.partner',
                                              compute='_compute_restricted_partner_ids',
                                              inverse='_inverse_restricted_partner_ids',
                                              string="Customers",
                                              help="If some contacts are attached to the current product,"
                                                   " then this could be just be sold to those customers")
    brand_partner_status = fields.Selection([('limited', 'Limited'), ('restricted', 'Restricted')])

    def _compute_restricted_partner_ids(self):
        """Apply the template's `restricted_partner_ids` to its variant"""
        for template in self:
            if template.product_variant_count == 1:
                template.restricted_partner_ids = template.product_variant_id.restricted_partner_ids
            else:
                template.restricted_partner_ids = False

    def _inverse_restricted_partner_ids(self):
        """Apply the variants's `restricted_partner_ids` to its template"""
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.restricted_partner_ids = self.restricted_partner_ids
