from odoo import models, api, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_uom', 'product_uom_qty')
    def _check_avoid_fractions(self):
        """If the uom category of a product has `avoid_sell_fractions` enabled, and the
        quantity is not an integer, display a warning"""
        if self.product_uom.category_id.avoid_sell_fractions:
            if int(self.product_uom_qty) != self.product_uom_qty:
                warning = {
                    'title': _('Invalid Product Quantity'),
                    'message': _("Your're trying to sell {} {} of the product {}.\n"
                                 " However the UoM for that product ( {} ) doesn't allow to"
                                 " sell floating point amounts of it. Please enter a non-decimal Ordered Qty.").format(self.product_uom_qty,
                                                                                                                       self.product_uom.name,
                                                                                                                       self.product_id.name,
                                                                                                                       self.product_uom.name),
                }
                return {'warning': warning}

    @api.model_create_multi
    def create(self, vals_list):
        """If the uom category of a product has `avoid_sell_fractions` enabled, and the
        quantity is not an integer, return an error that prevents the creation of the quotation"""
        lines = super(SaleOrderLine, self).create(vals_list)
        for line in lines:
            if line.product_uom.category_id.avoid_sell_fractions:
                if int(line.product_uom_qty) != line.product_uom_qty:
                    raise ValidationError(_("Your're trying to sell {} {} of the product {}.\n"
                                            " However the UoM for that product ( {} ) doesn't allow to"
                                            " sell floating point amounts of it. Please enter a non-decimal Ordered Qty.").format(line.product_uom_qty,
                                                                                                                                  line.product_uom.name,
                                                                                                                                  line.product_id.name,
                                                                                                                                  line.product_uom.name))
        return lines

    @api.multi
    def write(self, vals):
        """If the uom category of a product has `avoid_sell_fractions` enabled, and the
        quantity is not an integer, return an error that prevents saving the quotation when
        a change was made to the quantity or the uom"""
        res = super(SaleOrderLine, self).write(vals)
        if vals.get('product_uom'):
            uom_id = self.env['uom.uom'].browse(vals.get('product_uom'))
            if uom_id.category_id.avoid_sell_fractions:
                if vals.get('product_uom_qty') and (int(vals.get('product_uom_qty')) != vals.get('product_uom_qty')):
                    raise ValidationError(_("Your're trying to sell {} {}.\n"
                                            " However the UoM for that product ( {} ) doesn't allow to"
                                            " sell floating point amounts of it. Please enter a non-decimal Ordered Qty.").format(vals.get('product_uom_qty'),
                                                                                                                                  uom_id.name,
                                                                                                                                  uom_id.name))
                else:
                    for line in self:
                        if int(line.product_uom_qty) != line.product_uom_qty:
                            raise ValidationError(_("Your're trying to sell {} {} of the product {}.\n"
                                                    " However the UoM for that product ( {} ) doesn't allow to"
                                                    " sell floating point amounts of it. Please enter a non-decimal Ordered Qty.").format(line.product_uom_qty,
                                                                                                                                          line.product_uom.name,
                                                                                                                                          line.product_id.name,
                                                                                                                                          line.product_uom.name))
        elif vals.get('product_uom_qty'):
            for line in self:
                if line.product_uom.category_id.avoid_sell_fractions:
                    if int(vals.get('product_uom_qty')) != vals.get('product_uom_qty'):
                        raise ValidationError(_("Your're trying to sell {} {} of the product {}.\n"
                                                " However the UoM for that product ( {} ) doesn't allow to"
                                                " sell floating point amounts of it. Please enter a non-decimal Ordered Qty.").format(vals.get('product_uom_qty'),
                                                                                                                                      line.product_uom.name,
                                                                                                                                      line.product_id.name,
                                                                                                                                      line.product_uom.name))
        return res
